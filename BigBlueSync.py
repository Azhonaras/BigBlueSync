import os
import re
import threading
import subprocess
import urllib.request
import http.cookiejar
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
import customtkinter as ctk
from tkinter import filedialog
import imageio_ffmpeg

# --- BIGBLUESYNC DESIGN SYSTEM ---
COLOR_BASE       = "#0F172A"  # Deep slate background
COLOR_CARD       = "#1E293B"  # Card / container surface
COLOR_BORDER     = "#334155"  # Subtle borders
COLOR_INPUT_BG   = "#0B1120"  # Input field background
COLOR_TEXT_MAIN  = "#F8FAFC"  # High-contrast text
COLOR_TEXT_MUTED = "#94A3B8"  # Secondary label text
COLOR_ACCENT     = "#0284C7"  # Primary BigBlue accent
COLOR_ACCENT_HOV = "#0369A1"  # Accent hover
COLOR_ACCENT_LGT = "#38BDF8"  # Accent light highlight
COLOR_BTN_SEC    = "#334155"  # Secondary button background
COLOR_BTN_SEC_HOV= "#475569"  # Secondary button hover
COLOR_ERROR      = "#EF4444"  # Error alert red
COLOR_SUCCESS    = "#10B981"  # Success green

ctk.set_appearance_mode("Dark")


class BigBlueSyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BigBlueSync: BigBlueButton Video Downloader & Merger")
        self.geometry("620x650")
        self.configure(fg_color=COLOR_BASE)
        self.resizable(False, False)

        # Header Container
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(28, 16))

        self.header = ctk.CTkLabel(
            self.header_frame, 
            text="BigBlueSync", 
            font=("Segoe UI", 26, "bold"), 
            text_color=COLOR_ACCENT_LGT
        )
        self.header.pack()

        self.subtitle = ctk.CTkLabel(
            self.header_frame,
            text="BigBlueButton Stream Downloader & Zero-Loss Remuxer",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.subtitle.pack(pady=(2, 0))

        # Main Central Card
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color=COLOR_CARD, 
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=12
        )
        self.main_frame.pack(fill="both", expand=True, padx=35, pady=(0, 30))

        # URL Input Section
        self.url_label = ctk.CTkLabel(
            self.main_frame, 
            text="BIGBLUEBUTTON PLAYBACK URL", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLOR_TEXT_MUTED
        )
        self.url_label.pack(anchor="w", padx=25, pady=(20, 5))
        
        self.url_entry = ctk.CTkEntry(
            self.main_frame, 
            height=40, 
            font=("Segoe UI", 13),
            placeholder_text="https://your-institution.edu/playback/presentation/2.3/...",
            fg_color=COLOR_INPUT_BG, 
            text_color=COLOR_TEXT_MAIN, 
            border_color=COLOR_BORDER, 
            border_width=1, 
            corner_radius=8
        )
        self.url_entry.pack(fill="x", padx=25)

        # Output Directory Section
        self.dir_label = ctk.CTkLabel(
            self.main_frame, 
            text="SAVE DESTINATION", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLOR_TEXT_MUTED
        )
        self.dir_label.pack(anchor="w", padx=25, pady=(18, 5))
        
        self.dir_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dir_frame.pack(fill="x", padx=25)
        
        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, 
            height=40, 
            font=("Segoe UI", 13),
            fg_color=COLOR_INPUT_BG, 
            text_color=COLOR_TEXT_MAIN,
            border_color=COLOR_BORDER, 
            border_width=1, 
            corner_radius=8
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))

        self.browse_btn = ctk.CTkButton(
            self.dir_frame, 
            text="Browse", 
            width=85, 
            height=40,
            font=("Segoe UI", 12, "bold"), 
            fg_color=COLOR_BTN_SEC, 
            text_color=COLOR_TEXT_MAIN, 
            hover_color=COLOR_BTN_SEC_HOV, 
            corner_radius=8,
            command=self.browse_folder
        )
        self.browse_btn.pack(side="right")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, 
            height=10, 
            corner_radius=5,
            fg_color=COLOR_INPUT_BG, 
            progress_color=COLOR_ACCENT_LGT
        )
        self.progress_bar.pack(fill="x", padx=25, pady=(22, 8))
        self.progress_bar.set(0) 

        # Detailed Status Label
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="Ready. Paste a BigBlueButton recording link to begin.", 
            font=("Segoe UI", 11), 
            text_color=COLOR_TEXT_MUTED, 
            wraplength=480
        )
        self.status_label.pack(pady=(0, 15))

        # Merge Switch Option
        self.merge_switch = ctk.CTkSwitch(
            self.main_frame, 
            text="Auto-Merge Screen Video + Webcam Audio (Lossless)", 
            font=("Segoe UI", 12), 
            text_color=COLOR_TEXT_MAIN,
            progress_color=COLOR_ACCENT, 
            button_color=COLOR_TEXT_MAIN,
            button_hover_color=COLOR_ACCENT_LGT
        )
        self.merge_switch.pack(anchor="w", padx=25, pady=(0, 18))
        self.merge_switch.select() 

        # Primary Action Button
        self.dl_btn = ctk.CTkButton(
            self.main_frame, 
            text="Start Download & Sync", 
            height=46,
            font=("Segoe UI", 14, "bold"), 
            fg_color=COLOR_ACCENT, 
            text_color="#FFFFFF", 
            hover_color=COLOR_ACCENT_HOV, 
            corner_radius=8,
            command=self.start_download_thread
        )
        self.dl_btn.pack(fill="x", padx=25, pady=(0, 25))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, ctk.END)
            self.dir_entry.insert(0, folder)

    def update_ui_progress(self, message, percent, color=COLOR_TEXT_MUTED):
        self.status_label.configure(text=message, text_color=color)
        self.progress_bar.set(max(0.0, min(1.0, percent / 100.0)))
        self.update_idletasks()

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        output_dir = self.dir_entry.get().strip()

        if not url:
            self.update_ui_progress("Error: Please enter a valid BigBlueButton URL.", 0, COLOR_ERROR)
            return

        self.dl_btn.configure(state="disabled", fg_color=COLOR_BTN_SEC, text="DOWNLOADING...")
        thread = threading.Thread(target=self.download_logic, args=(url, output_dir), daemon=True)
        thread.start()

    def extract_meeting_id(self, playback_url):
        parsed = urlparse(playback_url)
        query = parse_qs(parsed.query)
        
        # Format 1: query parameter `meetingId`
        if "meetingId" in query and query["meetingId"]:
            return query["meetingId"][0]
        
        # Format 2: regex match for 40-54 char hex/alphanumeric meeting ID in path
        path_clean = parsed.path.rstrip("/")
        match = re.search(r'([a-f0-9]{40,54}|[a-zA-Z0-9_\-]{20,64})$', path_clean)
        if match:
            return match.group(1)

        # Fallback: last non-empty segment of path
        segments = [p for p in path_clean.split("/") if p]
        if segments:
            return segments[-1]
            
        return None

    def download_logic(self, playback_url, output_dir):
        try:
            self.after(0, self.update_ui_progress, "Analyzing URL & session...", 0, COLOR_TEXT_MAIN)
            parsed_url = urlparse(playback_url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            meeting_id = self.extract_meeting_id(playback_url)

            if not meeting_id:
                self.after(0, self.update_ui_progress, "Error: Could not extract Meeting ID from URL.", 0, COLOR_ERROR)
                self.reset_button()
                return

            prefix = f"BigBlueSync_{meeting_id[:10]}"
            webcams_url = f"{domain}/presentation/{meeting_id}/video/webcams.mp4"
            deskshare_url = f"{domain}/presentation/{meeting_id}/deskshare/deskshare.mp4"
            
            webcams_path = os.path.join(output_dir, f"{prefix}_webcams.mp4")
            deskshare_path = os.path.join(output_dir, f"{prefix}_deskshare.mp4")

            os.makedirs(output_dir, exist_ok=True)
            files_downloaded = 0
            
            # Session builder with SSL tolerance for institutional servers
            cj = http.cookiejar.CookieJar()
            ssl_context = ssl._create_unverified_context()
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ssl_context),
                urllib.request.HTTPCookieProcessor(cj)
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': playback_url
            }

            try:
                req = urllib.request.Request(playback_url, headers=headers)
                with opener.open(req, timeout=10) as resp:
                    resp.read(1024)
            except Exception as e:
                print(f"Session handshake note: {e}")

            # Download targets
            targets = [
                (webcams_url, webcams_path, "Webcam & Audio stream"),
                (deskshare_url, deskshare_path, "Deskshare / Screen stream")
            ]

            for url, file_path, label in targets:
                self.after(0, self.update_ui_progress, f"Connecting to {label}...", 0, COLOR_TEXT_MAIN)
                req = urllib.request.Request(url, headers=headers)
                
                try:
                    with opener.open(req, timeout=15) as response:
                        file_size = int(response.info().get('Content-Length', -1))
                        
                        with open(file_path, 'wb') as f:
                            downloaded = 0
                            chunks = 0
                            while True:
                                chunk = response.read(16384)
                                if not chunk: 
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                chunks += 1
                                
                                if chunks % 50 == 0:
                                    mb_down = downloaded / (1024 * 1024)
                                    if file_size > 0:
                                        percent = (downloaded / file_size) * 100
                                        mb_total = file_size / (1024 * 1024)
                                        msg = f"Downloading {label}: {mb_down:.1f} / {mb_total:.1f} MB ({percent:.1f}%)"
                                        self.after(0, self.update_ui_progress, msg, percent, COLOR_ACCENT_LGT)
                                    else:
                                        msg = f"Downloading {label}: {mb_down:.1f} MB"
                                        self.after(0, self.update_ui_progress, msg, 0, COLOR_ACCENT_LGT)

                        files_downloaded += 1
                except Exception as file_error:
                    print(f"Stream {label} skipped: {file_error}")
                    continue

            # Merge Processing
            if files_downloaded > 0:
                has_webcams = os.path.exists(webcams_path) and os.path.getsize(webcams_path) > 0
                has_deskshare = os.path.exists(deskshare_path) and os.path.getsize(deskshare_path) > 0

                if self.merge_switch.get() == 1 and has_webcams and has_deskshare:
                    self.after(0, self.update_ui_progress, "Merging screen video & webcam audio...", 100, COLOR_TEXT_MAIN)
                    
                    merged_path = os.path.join(output_dir, f"{prefix}_MERGED.mp4")
                    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                    
                    cmd = [
                        ffmpeg_exe, "-y",
                        "-i", deskshare_path, 
                        "-i", webcams_path,   
                        "-map", "0:v:0",      
                        "-map", "1:a:0",      
                        "-c:v", "copy",       
                        "-c:a", "copy",       
                        "-shortest",          
                        merged_path
                    ]
                    
                    try:
                        creationflags = 0x08000000 if os.name == 'nt' else 0
                        subprocess.run(cmd, creationflags=creationflags, capture_output=True, text=True, check=True)
                        self.after(0, self.update_ui_progress, "Complete! Lecture Downloaded & Merged Successfully.", 100, COLOR_SUCCESS)
                    except subprocess.CalledProcessError as ffmpeg_err:
                        err_msg = ffmpeg_err.stderr if ffmpeg_err.stderr else "Remux stream sync issue."
                        self.after(0, self.update_ui_progress, f"Merge Failed: {err_msg[:60]}", 100, COLOR_ERROR)
                else:
                    self.after(0, self.update_ui_progress, "Saved individual stream file(s) successfully.", 100, COLOR_SUCCESS)
            else:
                self.after(0, self.update_ui_progress, "Error: No downloadable streams found on the server.", 0, COLOR_ERROR)

        except Exception as general_error:
            self.after(0, self.update_ui_progress, f"Error: {str(general_error)[:60]}", 0, COLOR_ERROR)
        finally:
            self.reset_button()

    def reset_button(self):
        self.dl_btn.configure(state="normal", fg_color=COLOR_ACCENT, text="Start Download & Sync")


if __name__ == "__main__":
    app = BigBlueSyncApp()
    app.mainloop()
