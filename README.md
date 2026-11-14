# Folder LRC Generator

A Windows utility that creates a timed `.lrc` file beside each audio or video file.

## Download

Get **Folder.LRC.Generator.exe** from the [latest release](https://github.com/Itz-DevSB/folder-lrc-generator/releases/latest).

## Quick start

1. Download `Folder.LRC.Generator.exe` from the release assets.
2. Copy the EXE into the folder that contains your music or videos.
3. Double-click the EXE and let it finish. It scans that folder and all folders inside it.
4. Find each generated `.lrc` beside its matching media file. The scan report is saved beside the EXE.

You can also place the EXE in a main music folder to process its subfolders. You do not need to install Python or run `Setup.bat`.

## What it does

For each media file, the generator first looks for synchronized lyrics online. If it finds a match, it saves those lyrics and skips local transcription for that song. If no timed lyrics are found, the bundled Whisper engine transcribes the audio locally and estimates word or segment timestamps.

Supported formats include MP3, M4A, AAC, FLAC, WAV, OGG, OPUS, WMA, MP4, MKV, MOV, AVI, WEBM, M4V, WMV, MPEG, and MPG.

## Existing lyrics and retrying

If a matching `.lrc` file already exists, it is left unchanged and that media file is skipped. To try again, move or rename that `.lrc` file, then run the EXE again.

## First run and requirements

- Windows 10 or newer.
- Internet is used for online lyric lookup and to download the Whisper `base` model the first time local transcription is needed. The model is cached for later runs.
- Files with online timed lyrics skip Whisper, so those files do not need local transcription.

## Accuracy

Whisper supports Hindi and can detect the language automatically, but it is designed for speech. It may miss or mishear sung words, especially with music, accents, background vocals, or Hindi-English mixing. Timestamps are estimates and are not guaranteed to be perfectly synchronized. Online lyrics can also be missing or match another recording. Please review generated files.

## Privacy

Online lookup sends the song title and artist (from metadata when available, otherwise from the filename) and approximate duration to LRCLIB. The media file itself is not uploaded for lyric lookup. Whisper transcription runs locally; the model is downloaded from Hugging Face on first use.

## License and source

This project is distributed under GPL-2.0-or-later because the Windows executable bundles GPL-licensed components. The matching application source is in this repository. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The EXE is available from the [Releases page](https://github.com/Itz-DevSB/folder-lrc-generator/releases).
