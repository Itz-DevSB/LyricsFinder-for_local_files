# Third-party software notices

The Windows executable bundles open-source software. The program's own source
and the license for this combined distribution are provided in this repository.
The executable is offered under the GNU General Public License, version 2 or
any later version (GPL-2.0-or-later). This notice is a summary; each project’s
license text controls its component.

Known bundled components include:

| Component | Purpose | License / project |
| --- | --- | --- |
| Mutagen 1.48.1 | Reading media tags and duration | GPL-2.0-or-later — <https://github.com/quodlibet/mutagen> |
| PyAV | Media decoding for Whisper | BSD-3-Clause — <https://github.com/PyAV-Org/PyAV> |
| FFmpeg libraries distributed with PyAV | Audio/video codecs | LGPL/GPL components may be enabled in the Windows build, including x264; see <https://github.com/PyAV-Org/pyav-ffmpeg> and <https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md> |
| faster-whisper | Local speech transcription | MIT — <https://github.com/SYSTRAN/faster-whisper> |
| CTranslate2 | Whisper inference engine | MIT — <https://github.com/OpenNMT/CTranslate2> |
| PyInstaller | Packaging the Windows executable | GPL-2.0-or-later with a bootloader exception — <https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt> |

The executable also bundles transitive Python dependencies. Their license
texts and notices are available from the corresponding upstream projects and
package distributions. Refer to each upstream project for its complete license
and source. The included application source is the source used for this
release; build dependencies and packaging tools are identified above.

Whisper model files are downloaded from Hugging Face on first local
transcription and are not included in this executable. The model is separately
licensed by its publisher: <https://huggingface.co/Systran/faster-whisper-base>.

