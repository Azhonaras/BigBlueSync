# BigBlueSync

BigBlueButton recording downloader and stream multiplexer.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-0284C7.svg)](https://github.com/TomSchimansky/CustomTkinter)

---

## Overview

BigBlueSync is a desktop application for downloading and combining recorded BigBlueButton sessions into single video files.

BigBlueButton stores recordings in separate media streams, typically keeping screen shares in `deskshare.mp4` and microphone audio with camera video in `webcams.mp4`. BigBlueSync automatically downloads both files and runs a stream copy through FFmpeg to merge the screen recording with presenter audio into an `.mp4` file in seconds without quality loss.

---

## Download and run

Precompiled standalone binaries are available on the [Releases](https://github.com/Azhonaras/BigBlueSync/releases) page. No Python or dependencies required.

| Platform | File to download | How to run |
| :--- | :--- | :--- |
| **Windows** | `BigBlueSync-Windows.exe` | Double-click to run |
| **macOS** | `BigBlueSync-macOS` | Double-click or run from terminal |
| **Linux** | `BigBlueSync-Linux-x86_64` | `chmod +x BigBlueSync-Linux-x86_64 && ./BigBlueSync-Linux-x86_64` |

---

## Features

- **Lossless stream remuxing**: Combines video and audio streams using FFmpeg stream copy (`-c:v copy -c:a copy`), completing in seconds without quality loss.
- **URL resolver**: Automatically extracts meeting IDs from standard playback paths (`/playback/presentation/2.3/<id>`) and query parameters (`?meetingId=<id>`).
- **Dark mode interface**: Clean desktop interface with real-time status and progress tracking.
- **SSL tolerance**: Connects to institutional servers that use internal or self-signed SSL certificates.
- **Real-time progress**: Displays download progress in megabytes and percentage.
- **Bundled FFmpeg**: Includes required media processing tools with no configuration needed.

---

## Processing pipeline

```
                         BigBlueButton Playback URL
                                     │
                    Meeting ID & Server Host Extraction
                                     │
                ┌────────────────────┴────────────────────┐
                ▼                                         ▼
         webcams.mp4                              deskshare.mp4
   (Presenter Voice & Video)                  (Screen Share & Slides)
                │                                         │
                └────────────────────┬────────────────────┘
                                     ▼
                          FFmpeg Zero-Copy Remux
                       -map 0:v:0 (deskshare video)
                       -map 1:a:0 (webcam audio)
                       -c:v copy -c:a copy
                                     │
                                     ▼
                       BigBlueSync_<id>_MERGED.mp4
```

---

## Running from source (optional)

If you prefer to run from source code:

```bash
git clone https://github.com/Azhonaras/BigBlueSync.git
cd BigBlueSync
pip install -r requirements.txt
python BigBlueSync.py
```

---

## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for details.
