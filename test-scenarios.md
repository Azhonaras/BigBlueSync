# BigBlueSync — Manual QA Test Scenarios & Verification Matrix

> Grounded strictly in [`BigBlueSync.py`](./BigBlueSync.py) source code.

---

## 0. Environment Setup & Pre-Flight Matrix

| Component / Tool | Required State / Test Configuration | Rationale & Importance |
| :--- | :--- | :--- |
| **Python Runtime** | Python 3.10+ with `customtkinter` and `imageio_ffmpeg` | Bundled FFmpeg binary eliminates manual environment configuration. |
| **Network & SSL** | Active internet connection to test BigBlueButton endpoints | Bypasses self-signed institutional SSL certificates cleanly via `ssl._create_unverified_context()`. |
| **Clean Slate Reset** | `Remove-Item "$HOME\Downloads\BigBlueSync_*" -Force` | Clears pre-existing download and merged artifacts before testing. |

---

## 1. URL Parsing & Meeting ID Extraction

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `1.1.1` | Leave URL field empty, click **Start Download & Sync** | Status shows red text: `Error: Please enter a valid BigBlueButton URL.`. Progress bar remains at `0%`. No background thread is spawned. | [ ] |
| `1.1.2` | Enter whitespace only (`"   "`) in URL field | Status shows red text: `Error: Please enter a valid BigBlueButton URL.`. | [ ] |
| `1.1.3` | Enter arbitrary non-URL text (e.g. `invalid_string_123`) | Status shows red text: `Error: Could not extract Meeting ID from URL.`. Button resets to `Start Download & Sync`. | [ ] |
| `1.1.4` | Enter standard BBB 2.3 URL: `https://bbb.uni.edu/playback/presentation/2.3/d3b07384d113edec49eaa6238ad5ff00` | Extracts `meeting_id = d3b07384d113edec49eaa6238ad5ff00`. Status advances to `Analyzing URL & session...`. | [ ] |
| `1.1.5` | Enter URL with query parameter format: `https://bbb.uni.edu/playback.html?meetingId=a1b2c3d4e5f678901234567890abcdef12345678` | Extracts `meeting_id = a1b2c3d4e5f678901234567890abcdef12345678` without trailing query string artifacts. | [ ] |
| `1.1.6` | Enter URL with trailing slash: `https://bbb.uni.edu/playback/presentation/2.3/99a8b7c6d5e4/` | Trailing slash is stripped cleanly; extracts `99a8b7c6d5e4` without IndexErrors. | [ ] |

---

## 2. Destination Directory & File Browser

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `2.1.1` | Launch application and inspect default Save Destination | Pre-populates with standard user Downloads directory: `C:\Users\<User>\Downloads`. | [ ] |
| `2.1.2` | Click **Browse**, select a new folder, click **Select Folder** | Entry is cleared and updated with the chosen folder path. | [ ] |
| `2.1.3` | Click **Browse**, then click **Cancel** | Existing path remains untouched; no blanking occurs. | [ ] |
| `2.1.4` | Enter non-existent sub-folder path manually (e.g. `Downloads\BigBlueSync_Test`) | `os.makedirs(output_dir, exist_ok=True)` creates directory tree automatically. | [ ] |

---

## 3. Stream Acquisition & Download Ingestion

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `3.1.1` | Start download on valid BBB lecture URL | Status moves sequentially: `Analyzing URL & session...` → `Connecting to Webcam & Audio stream...` → live MB chunks → `Connecting to Deskshare / Screen stream...`. | [ ] |
| `3.1.2` | Verify chunked buffer read size during download | Streams in 16384-byte chunks; UI updates progress every 50 chunks without window freezing. | [ ] |
| `3.1.3` | Verify progress when Content-Length header is present | Displays: `Downloading <label>: X.X / Y.Y MB (Z.Z%)` with progress bar filling proportionally. | [ ] |
| `3.1.4` | Verify progress when Content-Length header is missing (-1) | Displays: `Downloading <label>: X.X MB` without division by zero crash. | [ ] |
| `3.1.5` | Provide URL where streams return HTTP 404 | Status shows red error: `Error: No downloadable streams found on the server.`. | [ ] |

---

## 4. Lossless FFmpeg Multiplexing & Merging

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `4.1.1` | Download with **Auto-Merge** switch ENABLED | FFmpeg executes `-map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest`. Remux takes ~2 seconds with zero loss. | [ ] |
| `4.1.2` | Inspect output file names in destination directory | Files created with prefix: `BigBlueSync_<10charsOfID>_MERGED.mp4`. Target directory contains the clean merged file. | [ ] |
| `4.1.3` | Verify Windows process flags during remuxing | Flag `0x08000000` (CREATE_NO_WINDOW) prevents black cmd.exe popup windows. | [ ] |
| `4.1.4` | Download with **Auto-Merge** switch DISABLED | Merging is skipped; raw `BigBlueSync_<id>_webcams.mp4` and `BigBlueSync_<id>_deskshare.mp4` remain. | [ ] |
| `4.1.5` | Download single-stream lecture (webcam only, no deskshare) | Merge step is safely bypassed; status reports `Saved individual stream file(s) successfully.`. | [ ] |

---

## 5. Concurrency & UI State Management

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `5.1.1` | Rapidly multi-click **Start Download & Sync** | Button immediately enters `disabled` state with label `DOWNLOADING...`. Exactly one thread is spawned. | [ ] |
| `5.1.2` | Drag / resize / minimize window during 500MB download | Window remains 100% responsive with zero "Not Responding" titlebar warnings. | [ ] |
| `5.1.3` | Observe button state after download completion or error | `finally` block triggers `reset_button()`; button returns to `normal` state, blue color `#0284C7`, and text `Start Download & Sync`. | [ ] |

---

## 6. End-to-End Journeys

| ID | Action / Input | Judgeable Expectation | Status |
| :--- | :--- | :--- | :---: |
| `6.1.1` | **Full Success Journey**: Valid BBB link → Destination folder → Merge on → Download | Progress bar reaches 100%, status shows green: `Complete! Lecture Downloaded & Merged Successfully.`. Merged MP4 plays in VLC with synced audio and screen video. | [ ] |
| `6.1.2` | **Failed Session Journey**: Invalid link → Download | Status shows red error within 2s, UI re-enables cleanly. | [ ] |

---

## 7. Regression Summary: An Error MUST Appear

| ID | Trigger / Condition | Required Error Message & Behavior |
| :--- | :--- | :--- |
| `7.1.1` | Empty or whitespace URL | `Error: Please enter a valid BigBlueButton URL.` |
| `7.1.2` | Unextractable URL | `Error: Could not extract Meeting ID from URL.` |
| `7.1.3` | Non-existent recording streams (404/403) | `Error: No downloadable streams found on the server.` |
| `7.1.4` | FFmpeg execution failure | `Merge Failed: <errorDetail>` |

---

## 8. Regression Summary: No Error MAY Appear

| ID | Normal Workflow Condition | Required Clean Behavior |
| :--- | :--- | :--- |
| `8.1.1` | Self-signed SSL institutional servers | Must not raise `ssl.SSLCertVerificationError`. |
| `8.1.2` | Missing `Content-Length` header on stream | Must not crash with `ZeroDivisionError`. |
| `8.1.3` | Canceling directory browse dialog | Must not raise exception or clear path. |
| `8.1.4` | FFmpeg execution on Windows | Must not pop up cmd.exe windows or flash taskbar. |
