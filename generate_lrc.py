#!/usr/bin/env python3
"""Fetch synchronized lyrics and locally transcribe media, then compare text."""
from __future__ import annotations
import difflib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MEDIA_EXTENSIONS = {".mp3", ".m4a", ".aac", ".flac", ".wav", ".ogg", ".opus", ".wma", ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".mpeg", ".mpg"}
_whisper_model = None

def read_tags(path):
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(path)
        if audio is None: return path.stem, "", None
        tags = audio.tags or {}
        def tag(*names):
            for name in names:
                value = tags.get(name)
                if value:
                    if hasattr(value, "text"): value = value.text
                    return str(value[0] if isinstance(value, (list, tuple)) else value).strip()
            return ""
        return tag("title", "TIT2", "©nam") or path.stem, tag("artist", "TPE1", "©ART", "albumartist"), float(audio.info.length) if audio.info else None
    except Exception: return path.stem, "", None

def lookup_synced_lyrics(title, artist, duration):
    params = {"track_name": title}
    if artist: params["artist_name"] = artist
    if duration: params["duration"] = str(round(duration))
    request = urllib.request.Request("https://lrclib.net/api/get?" + urllib.parse.urlencode(params), headers={"User-Agent": "FolderLRCGenerator/1.0 (local utility)"})
    try:
        with urllib.request.urlopen(request, timeout=12) as response: data = json.loads(response.read().decode("utf-8"))
        synced = data.get("syncedLyrics")
        rows = parse_lrc(synced or "")
        if rows: return rows
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError): pass
    # Exact lookup can miss when a file's tags or duration differ slightly.
    # Search by title and artist, then accept only a close title/artist match.
    params = {"track_name": title}
    if artist: params["artist_name"] = artist
    request = urllib.request.Request("https://lrclib.net/api/search?" + urllib.parse.urlencode(params), headers={"User-Agent": "FolderLRCGenerator/1.0 (local utility)"})
    try:
        with urllib.request.urlopen(request, timeout=12) as response: candidates = json.loads(response.read().decode("utf-8"))
        norm = lambda value: re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()
        best = None
        best_score = 0.0
        for candidate in candidates if isinstance(candidates, list) else []:
            candidate_title = candidate.get("trackName") or candidate.get("track_name") or ""
            candidate_artist = candidate.get("artistName") or candidate.get("artist_name") or ""
            title_score = difflib.SequenceMatcher(None, norm(title), norm(candidate_title)).ratio()
            artist_score = difflib.SequenceMatcher(None, norm(artist), norm(candidate_artist)).ratio() if artist else 1.0
            score = title_score * 0.7 + artist_score * 0.3
            if score > best_score and title_score >= 0.78 and artist_score >= (0.55 if artist else 0):
                rows = parse_lrc(candidate.get("syncedLyrics") or candidate.get("synced_lyrics") or "")
                if rows: best, best_score = rows, score
        return best
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError): return None

def parse_lrc(text):
    rows = []
    for line in text.splitlines():
        match = re.match(r"\[(\d{1,2}):(\d{2}(?:\.\d{1,3})?)\](.*)$", line.strip())
        if match: rows.append((int(match.group(1)) * 60 + float(match.group(2)), match.group(3).strip()))
    return rows or None

def transcribe(path):
    global _whisper_model
    try: from faster_whisper import WhisperModel
    except Exception as exc:
        if getattr(sys, "frozen", False):
            raise RuntimeError(f"The standalone app could not load its bundled Whisper engine ({type(exc).__name__}: {exc}). No Setup.bat is needed; replace this EXE with the latest build.") from exc
        raise RuntimeError("Local transcription is unavailable. Run Setup.bat.") from exc
    # faster-whisper 1.2.1 passes metadata_errors to av.open(), an option
    # removed by PyAV 19. Drop that obsolete option on newer PyAV versions.
    import av
    if int(av.__version__.split(".")[0]) >= 19 and not getattr(av.open, "_lrc_compat", False):
        original_open = av.open
        def compatible_open(*args, **kwargs):
            kwargs.pop("metadata_errors", None)
            return original_open(*args, **kwargs)
        compatible_open._lrc_compat = True
        av.open = compatible_open
    if _whisper_model is None:
        print("  Loading faster base Whisper model (first use may download about 150 MB)...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    def run(vad_filter):
        segments, _ = _whisper_model.transcribe(str(path), beam_size=1,
            vad_filter=vad_filter, word_timestamps=True, condition_on_previous_text=False)
        rows = []
        for segment in segments:
            segment_words = getattr(segment, "words", None) or []
            if segment_words:
                rows.extend((float(w.start), w.word.strip()) for w in segment_words if w.word.strip())
            elif segment.text.strip():
                rows.append((float(segment.start), segment.text.strip()))
        return rows
    rows = run(True)
    if not rows:
        print("  Retrying transcription with music-friendly decoding...")
        rows = run(False)
    return rows

def timestamp(seconds):
    cs = max(0, round(seconds * 100)); minutes, rest = divmod(cs, 6000); secs, fraction = divmod(rest, 100)
    return f"[{minutes:02d}:{secs:02d}.{fraction:02d}]"

def save_lrc(path, rows):
    path.write_text("\ufeff" + "\n".join(f"{timestamp(t)}{line}" for t, line in rows) + "\n", encoding="utf-8")

def words(rows):
    return re.findall(r"[a-z0-9]+", " ".join(line for _, line in rows).casefold())

def agreement_percent(online, transcript):
    a, b = words(online), words(transcript)
    if not a or not b: return None
    return 100 * difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()

def pause_before_close():
    if getattr(sys, "frozen", False):
        try: input("Press Enter to close...")
        except EOFError: pass

def main():
    args = sys.argv[1:]
    if "--check-whisper" in args:
        try:
            import av
            import ctranslate2
            from faster_whisper import WhisperModel
            print(f"Whisper bundled and ready. PyAV {av.__version__}; CTranslate2 {ctranslate2.__version__}.")
            return 0
        except Exception as exc:
            print(f"Whisper bundle check failed: {type(exc).__name__}: {exc}")
            return 1
    replace_existing = "--replace" in args
    folder = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    if "--folder" in args:
        i = args.index("--folder")
        if i + 1 < len(args): folder = Path(args[i + 1]).expanduser().resolve()
        args = args[:i] + args[i + 2:]
    recursive = "--top-folder-only" not in args
    args = [arg for arg in args if arg != "--top-folder-only"]
    candidates = folder.rglob("*") if recursive else folder.iterdir()
    media = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS)
    # Older launchers passed the folder path as a positional argument. Only
    # apply a file filter when the explicit --only option is present.
    requested = set(args[args.index("--only") + 1:]) if "--only" in args else set()
    if requested:
        media = [p for p in media if p.name in requested]
    if not media:
        print(f"No supported audio or video files found in: {folder}")
        pause_before_close()
        return 0
    print(f"Scanning {folder} (including subfolders: {'yes' if recursive else 'no'})\nFound {len(media)} media file(s). Online lookup AND local transcription will run for each.\n")
    results = []
    for index, path in enumerate(media, 1):
        display_name = path.relative_to(folder).as_posix()
        print(f"[{index}/{len(media)}] {display_name}")
        title, artist, duration = read_tags(path)
        online = lookup_synced_lyrics(title, artist, duration)
        print("  Online timed lyrics: found" if online else "  Online timed lyrics: not found")
        if online:
            transcript = None
            transcription_status = "skipped (online lyrics found)"
            print("  Local transcription: skipped (online timed lyrics found)")
        else:
            try:
                transcript = transcribe(path)
                transcription_status = "completed" if transcript else "no text detected"
                print(f"  Local transcription: {len(transcript)} timestamped words/segments")
            except Exception as exc:
                transcript = None
                transcription_status = f"failed: {exc}"
                print(f"  Local transcription failed: {exc}")
        score = agreement_percent(online, transcript) if online and transcript else None
        if score is not None: print(f"  Text agreement: {score:.1f}% (rough word-sequence similarity)")
        elif online and transcript: print("  Text agreement: unavailable")
        output = path.with_suffix(".lrc")
        status = "preserved existing LRC" if output.exists() else "no LRC created"
        if not output.exists() or replace_existing:
            preferred = online or transcript
            if preferred:
                try:
                    save_lrc(output, preferred)
                    status = ("updated from online lyrics" if online else "updated from local word-timed transcription") if output.exists() else ("created from online lyrics" if online else "created from local word-timed transcription")
                except OSError as exc: status = f"LRC write failed: {exc}"
        print(f"  LRC: {status}\n")
        results.append((display_name, bool(online), bool(transcript), score, status, transcription_status))

    report = folder / ("LRC retry comparison report.txt" if requested else "LRC comparison report.txt")
    both_scores = [r[3] for r in results if r[3] is not None]
    lines = ["LRC Generator: online lyrics vs local transcription", "Agreement is a rough word-sequence similarity, not an accuracy guarantee.", "", "Per-file results:"]
    for name, has_online, has_transcript, score, status, transcription_status in results:
        score_text = f"{score:.1f}%" if score is not None else "n/a"
        lines.append(f"{name} | online={'yes' if has_online else 'no'} | transcription={transcription_status} | agreement={score_text} | {status}")
    local_runs = sum(not r[1] for r in results)
    local_skips = sum(r[1] for r in results)
    lines += ["", f"Files scanned: {len(results)}", f"Online timed lyrics found: {sum(r[1] for r in results)}", f"Local fallback runs: {local_runs}", f"Local transcription skipped because online lyrics were found: {local_skips}", f"Both available for comparison: {len(both_scores)}", f"Average agreement where both were available: {sum(both_scores) / len(both_scores):.1f}%" if both_scores else "Average agreement: unavailable"]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Finished. Comparison report: {report.name}")
    print(f"Online matches: {sum(r[1] for r in results)}/{len(results)} | Local fallback runs: {local_runs} | Local runs skipped: {local_skips}")
    if both_scores: print(f"Average rough text agreement: {sum(both_scores) / len(both_scores):.1f}%")
    pause_before_close()
    return 0

if __name__ == "__main__": raise SystemExit(main())

