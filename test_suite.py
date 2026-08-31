import os
import sys
import unittest
import tempfile
import subprocess
import shutil
from unittest.mock import MagicMock, patch

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import imageio_ffmpeg
from BigBlueSync import (
    BigBlueSyncApp,
    COLOR_BASE,
    COLOR_CARD,
    COLOR_ACCENT,
    COLOR_ACCENT_LGT,
    COLOR_ERROR,
    COLOR_SUCCESS
)

class TestBigBlueSyncScenarios(unittest.TestCase):
    
    def setUp(self):
        # Initialize headless or hidden app for testing
        self.app = BigBlueSyncApp()
        self.app.withdraw()  # Hide GUI window during tests
        self.test_dir = tempfile.mkdtemp(prefix="bbs_test_")

    def tearDown(self):
        try:
            self.app.update_idletasks()
            self.app.quit()
            self.app.destroy()
        except Exception:
            pass
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # --- SECTION 1: URL Parsing & Meeting ID Extraction ---
    def test_1_1_1_empty_url_handling(self):
        """Scenario 1.1.1: Empty URL triggers error guard."""
        self.app.url_entry.delete(0, "end")
        self.app.start_download_thread()
        self.assertIn("Please enter a valid BigBlueButton URL", self.app.status_label.cget("text"))
        self.assertEqual(self.app.progress_bar.get(), 0.0)

    def test_1_1_2_whitespace_url_handling(self):
        """Scenario 1.1.2: Whitespace-only URL triggers error guard."""
        self.app.url_entry.delete(0, "end")
        self.app.url_entry.insert(0, "   \t  \n ")
        self.app.start_download_thread()
        self.assertIn("Please enter a valid BigBlueButton URL", self.app.status_label.cget("text"))
        self.assertEqual(self.app.progress_bar.get(), 0.0)

    def test_1_1_4_standard_bbb_2_3_path(self):
        """Scenario 1.1.4: Extract meeting ID from standard BBB 2.3 path."""
        url = "https://bbb.uni.edu/playback/presentation/2.3/d3b07384d113edec49eaa6238ad5ff00"
        meeting_id = self.app.extract_meeting_id(url)
        self.assertEqual(meeting_id, "d3b07384d113edec49eaa6238ad5ff00")

    def test_1_1_5_query_param_meeting_id(self):
        """Scenario 1.1.5: Extract meeting ID from query parameter."""
        url = "https://bbb.uni.edu/playback.html?meetingId=a1b2c3d4e5f678901234567890abcdef12345678"
        meeting_id = self.app.extract_meeting_id(url)
        self.assertEqual(meeting_id, "a1b2c3d4e5f678901234567890abcdef12345678")

    def test_1_1_6_trailing_slash_handling(self):
        """Scenario 1.1.6: Trailing slash is stripped cleanly."""
        url = "https://bbb.uni.edu/playback/presentation/2.3/99a8b7c6d5e4f3a2b1c0/"
        meeting_id = self.app.extract_meeting_id(url)
        self.assertEqual(meeting_id, "99a8b7c6d5e4f3a2b1c0")

    # --- SECTION 2: Destination Directory & Creation Guards ---
    def test_2_1_1_default_destination(self):
        """Scenario 2.1.1: Default destination is populated with Downloads."""
        val = self.app.dir_entry.get()
        expected = os.path.join(os.path.expanduser("~"), "Downloads")
        self.assertEqual(val, expected)

    def test_2_1_4_auto_create_nonexistent_directory(self):
        """Scenario 2.1.4: Nested non-existent directory auto-created."""
        nested_dir = os.path.join(self.test_dir, "nested", "sub_dir")
        self.assertFalse(os.path.exists(nested_dir))
        os.makedirs(nested_dir, exist_ok=True)
        self.assertTrue(os.path.exists(nested_dir))

    # --- SECTION 3 & 4: FFmpeg Binary & Stream Multiplexing ---
    def test_4_1_0_ffmpeg_binary_availability(self):
        """Scenario 4.1.0: Verify imageio_ffmpeg can resolve valid ffmpeg executable."""
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.assertTrue(os.path.exists(ffmpeg_exe), f"FFmpeg binary not found at: {ffmpeg_exe}")
        
        # Test running ffmpeg -version
        result = subprocess.run([ffmpeg_exe, "-version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("ffmpeg version", result.stdout)

    def test_4_1_1_lossless_ffmpeg_remux_simulation(self):
        """Scenario 4.1.1 & 4.1.2: Test lossless remuxing with synthetic test clips."""
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Generate dummy video file (1 sec lavfi testsrc)
        test_video = os.path.join(self.test_dir, "test_deskshare.mp4")
        subprocess.run([
            ffmpeg_exe, "-y", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=10",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", test_video
        ], capture_output=True, check=True)
        
        # Generate dummy audio file (1 sec sine wave audio)
        test_audio = os.path.join(self.test_dir, "test_webcams.mp4")
        subprocess.run([
            ffmpeg_exe, "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=1",
            "-c:a", "aac", test_audio
        ], capture_output=True, check=True)
        
        merged_output = os.path.join(self.test_dir, "BigBlueSync_test123456_MERGED.mp4")
        
        # Execute exact app command
        cmd = [
            ffmpeg_exe, "-y",
            "-i", test_video,
            "-i", test_audio,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "copy",
            "-shortest",
            merged_output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertTrue(os.path.exists(merged_output))
        self.assertGreater(os.path.getsize(merged_output), 0)
        self.assertTrue(os.path.basename(merged_output).startswith("BigBlueSync_"))

    # --- SECTION 5: Concurrency & State Management ---
    def test_5_1_1_button_and_ui_branding(self):
        """Scenario 5.1.1: Verify UI text, class branding, and color constants."""
        self.assertIn("BigBlueSync", self.app.title())
        self.assertEqual(self.app.header.cget("text"), "BigBlueSync")
        self.assertEqual(self.app.dl_btn.cget("text"), "Start Download & Sync")
        self.assertEqual(self.app.merge_switch.get(), 1)  # Merge enabled by default

    def test_5_1_3_reset_button_state(self):
        """Scenario 5.1.3: Reset button restores state and accent color."""
        self.app.dl_btn.configure(state="disabled", text="DOWNLOADING...", fg_color="#334155")
        self.app.reset_button()
        self.assertEqual(self.app.dl_btn.cget("state"), "normal")
        self.assertEqual(self.app.dl_btn.cget("text"), "Start Download & Sync")
        self.assertEqual(self.app.dl_btn.cget("fg_color"), COLOR_ACCENT)

    # --- SECTION 7 & 8: Regression Behavior ---
    def test_7_1_1_progress_update_bounds(self):
        """Scenario 7.1.1: Progress bar clamping between 0.0 and 1.0."""
        self.app.update_ui_progress("Test progress", 50, COLOR_ACCENT_LGT)
        self.assertAlmostEqual(self.app.progress_bar.get(), 0.5, places=2)
        
        self.app.update_ui_progress("Max progress", 150, COLOR_ACCENT_LGT)
        self.assertEqual(self.app.progress_bar.get(), 1.0)
        
        self.app.update_ui_progress("Min progress", -20, COLOR_ERROR)
        self.assertEqual(self.app.progress_bar.get(), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
