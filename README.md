# BigBlueSync

BigBlueButton recording downloader and stream multiplexer.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-0284C7.svg)](https://github.com/TomSchimansky/CustomTkinter)

---

## Overview

BigBlueSync is a desktop utility for downloading and combining recorded BigBlueButton sessions into single video files.

BigBlueButton stores recordings in separate media streams, typically keeping screen shares in `deskshare.mp4` and microphone audio with camera video in `webcams.mp4`. BigBlueSync downloads both files and runs a stream copy through FFmpeg to mux the screen recording with the presenter audio into an `.mp4` file without re-encoding.

---

## Features

- **Lossless stream remuxing**: Combines video and audio streams using FFmpeg stream copy (`-c:v copy -c:a copy`), completing in a few seconds without quality loss.
- **URL resolver**: Extracts meeting IDs from standard playback paths (`/playback/presentation/2.3/<id>`) and query parameters (`?meetingId=<id>`).
- **Dark mode interface**: Built on CustomTkinter with responsive status feedback and progress tracking.
- **SSL tolerance**: Connects to institutional servers that use internal or self-signed SSL certificates.
- **Download progress**: Displays real-time chunk progress in megabytes and percentage.
- **Bundled FFmpeg support**: Uses `imageio-ffmpeg` to manage FFmpeg binaries without requiring manual PATH configuration.

---

## Quick start

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/BigBlueSync.git
cd BigBlueSync
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python BigBlueSync.py
```

---

## Building a standalone executable

To compile BigBlueSync into a single Windows executable:

```bash
pyinstaller --clean BigBlueSync.spec
```

The output binary is placed in the `dist/` directory as `BigBlueSync.exe`.

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

## Testing and verification

BigBlueSync includes automated unit and integration tests along with an interactive manual QA checklist:

### Run automated tests
```bash
python test_suite.py
```

### Open manual QA test book
Open `scenarios.html` in any modern web browser to track test cases with persistent browser storage.

---

## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for details.
