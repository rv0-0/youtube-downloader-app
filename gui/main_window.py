"""
Main window for the YouTube Downloader GUI
Coordinates all components and handles message processing
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import queue
import os

from .constants import (
    DEFAULT_WINDOW_SIZE, DEFAULT_MIN_SIZE, DEFAULT_DOWNLOAD_PATH,
    MAIN_BG_COLOR, SECONDARY_BG_COLOR, MESSAGE_UPDATE_INTERVAL
)
from .ui_components import UIComponents
from .progress_tracker import ProgressTracker
from .download_manager import DownloadManager


class YouTubeDownloaderGUI:
    """Main GUI window for the YouTube Downloader"""
    
    def __init__(self):
        # Setup main window
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(*DEFAULT_MIN_SIZE)
        self.root.configure(bg=MAIN_BG_COLOR)
        
        # Initialize components
        self.download_path = DEFAULT_DOWNLOAD_PATH
        self.message_queue = queue.Queue()
        
        # Create string variables for progress display
        overall_progress_var = tk.StringVar(value="Ready")
        current_progress_var = tk.StringVar(value="No active download")
        
        # Initialize managers (progress bars will be created by UI components)
        self.progress_tracker = ProgressTracker(
            videos_tree=None,  # Will be set in UI setup
            overall_progress_bar=None,  # Will be set in UI setup
            current_progress_bar=None,  # Will be set in UI setup
            overall_progress_var=overall_progress_var,
            current_progress_var=current_progress_var
        )
        
        self.download_manager = DownloadManager(self.message_queue)
        
        # Initialize UI components
        self.ui = UIComponents(self.root, self.progress_tracker)
        
        # Setup UI
        self.setup_ui()
        
        # Start message processing
        self.update_messages()
    
    def setup_ui(self):
        """Setup the complete user interface"""
        self.ui.setup_ui(
            download_path=self.download_path,
            browse_callback=self.browse_folder,
            clear_callback=self.clear_urls,
            quality_change_callback=self.on_quality_change
        )
        
        # Connect button callbacks
        self.ui.download_button.config(command=self.start_download)
        self.ui.stop_button.config(command=self.stop_download)
        
        # Update path variable when download path changes
        self.ui.path_var.trace('w', self.on_path_change)
    
    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.ui.path_var.set(folder)
    
    def on_path_change(self, *args):
        """Handle download path change"""
        self.download_path = self.ui.path_var.get()
    
    def clear_urls(self):
        """Clear the URLs text area"""
        self.ui.clear_urls()
    
    def on_quality_change(self, event=None):
        """Handle quality selection change"""
        self.ui.on_quality_change(event)
    
    def start_download(self):
        """Start the download process"""
        urls_text = self.ui.get_urls_text()
        if not urls_text:
            messagebox.showwarning("No URLs", "Please enter at least one YouTube URL")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        invalid_urls = [url for url in urls if 'youtube.com' not in url and 'youtu.be' not in url]
        
        if invalid_urls:
            messagebox.showwarning("Invalid URLs", 
                                 f"Found {len(invalid_urls)} invalid YouTube URLs. "
                                 "Please check your URLs and try again.")
            return
        
        # Update UI state
        self.ui.set_download_buttons_state(download_enabled=False, stop_enabled=True)
        self.ui.clear_log()
        self.progress_tracker.clear_video_progress()
        self.progress_tracker.reset_progress_bars()
        
        # Initialize progress tracking
        self.progress_tracker.total_videos = len(urls)
        self.progress_tracker.current_video_index = 0
        
        # Pre-populate video list for single URLs
        for i, url in enumerate(urls, 1):
            self.progress_tracker.add_video_to_progress(i, f"Video {i}", url)
        
        # Update progress display
        self.progress_tracker.overall_progress_var.set(f"Starting download of {len(urls)} URLs...")
        self.progress_tracker.current_progress_var.set("Initializing...")
        
        # Get download settings
        settings = self.ui.get_download_settings()
        
        # Start download
        self.download_manager.start_download(urls, settings, self.progress_tracker)
        self.ui.log_message(f"🚀 Starting download of {len(urls)} URLs...")
    
    def stop_download(self):
        """Stop the download process"""
        self.ui.log_message("⏹️ Stopping download...", "orange")
        self.progress_tracker.overall_progress_var.set("Stopping download...")
        self.progress_tracker.current_progress_var.set("Stopping...")
        
        # Stop the download manager
        self.download_manager.stop_download()
        
        # Update UI state
        self.progress_tracker.overall_progress_var.set("Download stopped")
        self.progress_tracker.current_progress_var.set("Stopped")
        self.ui.set_download_buttons_state(download_enabled=True, stop_enabled=False)
        self.ui.log_message("❌ Download stopped by user")
    
    def update_messages(self):
        """Process messages from download thread"""
        try:
            message_count = 0
            while True:
                message_type, *data = self.message_queue.get_nowait()
                message_count += 1
                
                if message_type == "log":
                    self.ui.log_message(data[0])
                
                elif message_type == "video_progress":
                    progress_data = data[0]
                    self.progress_tracker.update_video_progress(
                        url=progress_data["url"],
                        status=progress_data.get("status"),
                        progress=progress_data.get("progress"),
                        title=progress_data.get("title")
                    )
                    self.progress_tracker.update_overall_progress()
                
                elif message_type == "current_progress":
                    if len(data) >= 2:
                        self.progress_tracker.update_current_progress(data[0], data[1])
                    else:
                        self.progress_tracker.update_current_progress(data[0])
                
                elif message_type == "overall_progress":
                    self.progress_tracker.overall_progress_var.set(data[0])
                
                elif message_type == "complete":
                    completion_data = data[0]
                    self._handle_download_completion(completion_data)
                
                elif message_type == "error":
                    self.ui.log_message(f"❌ Error: {data[0]}")
                    self.ui.set_download_buttons_state(download_enabled=True, stop_enabled=False)
                
                # Limit processing to avoid UI freezing
                if message_count >= 50:
                    break
                    
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(MESSAGE_UPDATE_INTERVAL, self.update_messages)
    
    def _handle_download_completion(self, completion_data):
        """Handle download completion"""
        successful = completion_data["successful"]
        failed = completion_data["failed"]
        total = completion_data["total"]
        
        # Update UI state
        self.ui.set_download_buttons_state(download_enabled=True, stop_enabled=False)
        
        # Update progress display
        self.progress_tracker.overall_progress_var.set(f"✅ Complete: {successful}/{total} successful")
        self.progress_tracker.current_progress_var.set("Download completed")
        
        # Log completion
        if failed > 0:
            self.ui.log_message(f"⚠️ Download completed with {failed} failures")
        else:
            self.ui.log_message(f"✅ All downloads completed successfully!")
        
        # Show completion dialog
        if successful > 0:
            completion_message = f"Download completed!\\n\\n"
            completion_message += f"✅ Successful: {successful}\\n"
            if failed > 0:
                completion_message += f"❌ Failed: {failed}\\n"
            completion_message += f"📁 Files saved to: {self.download_path}"
            
            if failed > 0:
                completion_message += "\\n\\n💡 Tips for failed downloads:"
                completion_message += "\\n• Check if videos are private/unavailable"
                completion_message += "\\n• Try using cookies for age-restricted content"
                completion_message += "\\n• Verify your internet connection"
            
            messagebox.showinfo("Download Complete", completion_message)
        else:
            messagebox.showerror("Download Failed", 
                               "All downloads failed. Please check the logs for details.")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main function for GUI"""
    try:
        app = YouTubeDownloaderGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
