# Folder LRC Generator

A Windows utility that creates an `.lrc` lyric file beside each audio or video file.

## Use

1. Copy `Folder LRC Generator.exe` into the top folder of your music or video library.
2. Double-click the executable.
3. Wait for the scan to finish. Matching `.lrc` files are saved beside their media files; a comparison report is saved in the folder where the executable is located.

The program scans subfolders recursively. Existing `.lrc` files are left alone.

## How lyric lookup works

The program looks for synchronized lyrics online first. When it finds them, it skips Whisper for that track. If no online match is found, it uses the bundled Whisper engine locally to transcribe the audio and create timestamped text. The fallback uses word timestamps where available, but recognition and timing can be inaccurate, especially for singing. Review generated files.

## Requirements and first run

- Windows 10 or newer.
- An internet connection for online lyric lookup and the first Whisper model download. The Whisper model is downloaded automatically and cached on the computer; Python and a separate setup program are not required.
- Scanning the whole library may take time when many tracks need local transcription.

## Privacy

For online lyric lookup, the program sends the track title and artist (from metadata when available, otherwise from the filename) to LRCLIB. It does not upload the media file for lyric lookup. Whisper transcription runs locally.

## Limitations

- Online lyrics may be missing or may match a different recording.
- Whisper is designed for speech transcription; sung words can be missed or incorrect.
- Timestamps are estimates, not a guarantee of perfect synchronization.
- The report's text-agreement score is only a rough comparison when both sources are available; it is not a verified accuracy score.

## License and source

This project is distributed under GPL-2.0-or-later because the standalone Windows build bundles GPL-licensed components. The matching application source is in this repository. See LICENSE and THIRD_PARTY_NOTICES.md for details. The Windows executable is published as a downloadable asset on the Releases page.


