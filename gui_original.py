"""
GUI version of the YouTube Downloader using tkinter
Enhanced with quality selection and individual video progress tracking
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import sys
import subprocess
import signal
import os
import time
import traceback
from pathlib import Path
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("Warning: psutil not available. Process termination may be limited.")
    PSUTIL_AVAILABLE = False
try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import our YouTube downloader
from youtube_downloader import YouTubeDownloader


class YouTubeDownloaderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry("800x650")  # More compact size
        self.root.minsize(700, 500)  # Minimum size
        
        # Configure window style
        self.root.configure(bg='#f8f9fa')
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Downloader instance
        self.downloader = None
        self.download_path = "Downloads"
        self.download_stopped = False  # Flag to track if download was stopped
        
        # Process tracking for proper termination
        self.running_processes = []
        self.download_thread = None
        
        # Video progress tracking
        self.video_progress = {}
        self.current_video_index = 0
        self.total_videos = 0
        
        # Quality options - Updated for proper audio+video merging with ffmpeg
        self.quality_options = {
            "Best Quality (4K/1440p/1080p)": "bv*+ba/b",
            "High Quality (1080p max)": "bv*[height<=1080]+ba/b[height<=1080]",
            "Medium Quality (720p max)": "bv*[height<=720]+ba/b[height<=720]", 
            "Low Quality (480p max)": "bv*[height<=480]+ba/b[height<=480]",
            "Premium Quality (VP9+Opus)": "bv*[vcodec^=vp9]+ba[acodec^=opus]/bv*+ba/b",
            "Ultra Quality (AV1+Opus)": "bv*[vcodec^=av01]+ba[acodec^=opus]/bv*+ba/b",
            "Audio Only (Best)": "ba[ext=m4a]/ba[ext=mp3]/ba/b",
            "Custom Format": "custom"
        }
        
        self.setup_ui()
        self.update_messages()
    
    def setup_ui(self):
        """Setup the user interface - Clean and compact design"""
        # Configure main window style
        self.root.configure(bg='#f0f0f0')
        
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Configure grid weights for responsive design
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(6, weight=1)  # Video progress area
        main_container.rowconfigure(7, weight=1)  # Log area
        
        # Title - more compact
        title_label = ttk.Label(main_container, text="🎬 YouTube Downloader", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        
        # Top panel - Settings in a compact horizontal layout
        settings_panel = ttk.Frame(main_container)
        settings_panel.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        settings_panel.columnconfigure(1, weight=1)
        
        # Download path - more compact
        ttk.Label(settings_panel, text="📁 Path:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar(value=self.download_path)
        path_entry = ttk.Entry(settings_panel, textvariable=self.path_var, state="readonly", width=40)
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        browse_button = ttk.Button(settings_panel, text="Browse", command=self.browse_folder, width=8)
        browse_button.grid(row=0, column=2, sticky=tk.W)
        
        # Quality and subtitle options in same row
        options_panel = ttk.Frame(main_container)
        options_panel.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_panel.columnconfigure(1, weight=1)
        
        # Quality selection - compact
        ttk.Label(options_panel, text="🎥 Quality:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="Best Quality (4K/1440p/1080p)")
        quality_combo = ttk.Combobox(options_panel, textvariable=self.quality_var, 
                                   values=list(self.quality_options.keys()), 
                                   state="readonly", width=25)
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 15))
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)
        
        # Subtitle options - compact checkboxes
        self.download_subtitles_var = tk.BooleanVar(value=True)
        subtitle_check = ttk.Checkbutton(options_panel, text="📝 Subtitles", 
                                        variable=self.download_subtitles_var)
        subtitle_check.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.embed_subtitles_var = tk.BooleanVar(value=False)
        embed_check = ttk.Checkbutton(options_panel, text="📎 Embed", 
                                     variable=self.embed_subtitles_var)
        embed_check.grid(row=0, column=3, sticky=tk.W)
        
        # Custom format entry (initially hidden)
        self.custom_format_frame = ttk.Frame(main_container)
        self.custom_format_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        self.custom_format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.custom_format_frame, text="⚙️ Custom:").grid(row=0, column=0, sticky=tk.W)
        self.custom_format_var = tk.StringVar(value="bv*+ba/b")
        self.custom_format_entry = ttk.Entry(self.custom_format_frame, textvariable=self.custom_format_var)
        self.custom_format_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        help_button = ttk.Button(self.custom_format_frame, text="?", width=3, 
                               command=self.show_format_help)
        help_button.grid(row=0, column=2, sticky=tk.W)
        
        # Hide custom format initially
        self.custom_format_frame.grid_remove()
        
        
        # URLs input - more compact
        urls_panel = ttk.LabelFrame(main_container, text="🔗 YouTube URLs", padding="8")
        urls_panel.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))
        urls_panel.columnconfigure(0, weight=1)
        urls_panel.rowconfigure(0, weight=1)
        
        self.urls_text = scrolledtext.ScrolledText(urls_panel, height=4, width=50, 
                                                  font=("Consolas", 9))
        self.urls_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons - horizontal layout, more compact
        buttons_panel = ttk.Frame(main_container)
        buttons_panel.grid(row=5, column=0, pady=(0, 8))
        
        self.download_button = ttk.Button(buttons_panel, text="🚀 Start Download", 
                                         command=self.start_download, width=15)
        self.download_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.stop_button = ttk.Button(buttons_panel, text="⏹️ Stop", 
                                     command=self.stop_download, state="disabled", width=10)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 8))
        
        clear_button = ttk.Button(buttons_panel, text="🗑️ Clear", 
                                 command=self.clear_urls, width=10)
        clear_button.pack(side=tk.LEFT)
        
        
        # Progress section - compact design
        progress_panel = ttk.LabelFrame(main_container, text="📊 Progress", padding="8")
        progress_panel.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))
        progress_panel.columnconfigure(0, weight=1)
        progress_panel.rowconfigure(2, weight=1)
        
        # Overall progress - compact
        overall_frame = ttk.Frame(progress_panel)
        overall_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 4))
        overall_frame.columnconfigure(1, weight=1)
        
        ttk.Label(overall_frame, text="Overall:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.overall_progress_var = tk.StringVar(value="Ready")
        overall_label = ttk.Label(overall_frame, textvariable=self.overall_progress_var, 
                                 font=("Segoe UI", 9))
        overall_label.grid(row=0, column=1, sticky=tk.W, padx=(8, 0))
        
        self.overall_progress_bar = ttk.Progressbar(progress_panel, mode='determinate')
        self.overall_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Video progress treeview - more compact
        columns = ("Index", "Title", "Status", "Progress")
        self.videos_tree = ttk.Treeview(progress_panel, columns=columns, show="headings", height=6)
        
        # Configure column headings and widths
        self.videos_tree.heading("Index", text="#")
        self.videos_tree.heading("Title", text="Video Title")
        self.videos_tree.heading("Status", text="Status")
        self.videos_tree.heading("Progress", text="Progress")
        
        self.videos_tree.column("Index", width=40, anchor="center")
        self.videos_tree.column("Title", width=300)
        self.videos_tree.column("Status", width=100, anchor="center")
        self.videos_tree.column("Progress", width=80, anchor="center")
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(progress_panel)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.videos_tree.grid(row=0, column=0, in_=tree_frame, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.videos_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.videos_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        
        # Log section - compact and clean
        log_panel = ttk.LabelFrame(main_container, text="📝 Download Log", padding="8")
        log_panel.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_panel.columnconfigure(0, weight=1)
        log_panel.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_panel, height=6, width=50, 
                                                 font=("Consolas", 8), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add current progress display in the progress panel
        current_frame = ttk.Frame(progress_panel)
        current_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(4, 0))
        current_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_frame, text="Current:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.current_progress_var = tk.StringVar(value="No active download")
        current_label = ttk.Label(current_frame, textvariable=self.current_progress_var, 
                                 font=("Segoe UI", 9))
        current_label.grid(row=0, column=1, sticky=tk.W, padx=(8, 0))
        
        self.current_progress_bar = ttk.Progressbar(progress_panel, mode='determinate')
        self.current_progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
    
    def on_quality_change(self, event=None):
        """Handle quality selection change"""
        if self.quality_var.get() == "Custom Format":
            self.custom_format_frame.grid()
        else:
            self.custom_format_frame.grid_remove()
    
    def show_format_help(self):
        """Show help dialog for custom format"""
        help_text = """🎥 Custom Format Examples:

🏆 BEST QUALITY (With FFmpeg):
• bv*+ba/b - Best video + audio (recommended)
• bv*[ext=mp4]+ba[ext=m4a]/b - MP4 video + M4A audio
• bv*[vcodec^=vp9]+ba[acodec^=opus]/bv*+ba - VP9 + Opus

📺 RESOLUTION LIMITS:
• bv*[height<=1080]+ba/b[height<=1080] - Max 1080p
• bv*[height<=720]+ba/b[height<=720] - Max 720p

🎵 AUDIO ONLY:
• ba[ext=m4a]/ba - M4A audio
• ba[ext=mp3]/ba - MP3 audio

⚙️ ADVANCED:
• bv*[vcodec^=av01]+ba[acodec^=opus] - AV1 + Opus
• worst - Lowest quality (testing)

💡 'bv*+ba' = Best video + best audio with automatic fallback
📦 FFmpeg installed - high quality merging available!"""
        
        messagebox.showinfo("Format Help", help_text)
    
    def get_selected_format(self):
        """Get the currently selected video format"""
        quality_name = self.quality_var.get()
        if quality_name == "Custom Format":
            return self.custom_format_var.get()
        else:
            return self.quality_options.get(quality_name, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best")
    
    def clear_video_progress(self):
        """Clear the video progress tree"""
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        self.video_progress = {}
        self.current_video_index = 0
        self.total_videos = 0
    
    def add_video_to_progress(self, index, title, url):
        """Add a video to the progress tracking tree"""
        print(f"[GUI DEBUG] add_video_to_progress called:")
        print(f"  Index: {index}")
        print(f"  Title: {title}")
        print(f"  URL: {url}")
        
        # Check if this URL is already being tracked (avoid duplicates)
        if url in self.video_progress:
            print(f"[GUI DEBUG] URL already exists in progress tracking, skipping: {url}")
            return self.video_progress[url]["item_id"]
        
        # For playlist videos, don't use the total_videos in the display index
        # as it may not be updated yet when playlist videos are being added
        display_index = str(index) if isinstance(index, str) else f"{index}"
        
        # Compact display with shorter title
        display_title = title[:40] + "..." if len(title) > 40 else title
        
        item_id = self.videos_tree.insert("", "end", values=(
            display_index,
            display_title,
            "Pending",
            "0%"
        ))
        
        self.video_progress[url] = {
            "item_id": item_id,
            "index": index,
            "title": title,
            "status": "Pending",
            "progress": 0
        }
        
        print(f"[GUI DEBUG] Video added to progress tracking:")
        print(f"  Item ID: {item_id}")
        print(f"  Total videos in tracking: {len(self.video_progress)}")
        
        return item_id
    
    def update_video_progress(self, url, status=None, progress=None, quality=None, title=None):
        """Update progress for a specific video"""
        # Debug logging
        print(f"[GUI DEBUG] update_video_progress called:")
        print(f"  URL: {url}")
        print(f"  Status: {status}")
        print(f"  Progress: {progress}")
        print(f"  Quality: {quality}")
        print(f"  Title: {title}")
        
        # Check for exact URL match first
        if url in self.video_progress:
            video_info = self.video_progress[url]
            item_id = video_info["item_id"]
            print(f"[GUI DEBUG] Found exact URL match, item_id: {item_id}")
        else:
            # Check for URL variants (with/without parameters, different formats)
            print(f"[GUI DEBUG] No exact URL match found. Checking variants...")
            print(f"[GUI DEBUG] Available URLs in tracking: {len(self.video_progress)} total")
            
            matched_url = None
            for key in self.video_progress.keys():
                # Try to match by video ID (extract from URL)
                try:
                    if 'youtube.com/watch?v=' in url and 'youtube.com/watch?v=' in key:
                        url_id = url.split('watch?v=')[1].split('&')[0]
                        key_id = key.split('watch?v=')[1].split('&')[0]
                        if url_id == key_id:
                            matched_url = key
                            print(f"[GUI DEBUG] Found URL match by video ID: {url_id}")
                            break
                    elif 'youtu.be/' in url or 'youtu.be/' in key:
                        # Handle youtu.be short URLs
                        if 'youtu.be/' in url:
                            url_id = url.split('youtu.be/')[1].split('?')[0]
                        else:
                            url_id = url.split('watch?v=')[1].split('&')[0]
                        
                        if 'youtu.be/' in key:
                            key_id = key.split('youtu.be/')[1].split('?')[0]
                        else:
                            key_id = key.split('watch?v=')[1].split('&')[0]
                        
                        if url_id == key_id:
                            matched_url = key
                            print(f"[GUI DEBUG] Found URL match by video ID (youtu.be): {url_id}")
                            break
                except Exception as e:
                    print(f"[GUI DEBUG] Error parsing URL {key}: {e}")
                    continue
            
            if matched_url:
                url = matched_url  # Use the matched URL for the rest of the function
                video_info = self.video_progress[url]
                item_id = video_info["item_id"]
                print(f"[GUI DEBUG] Using matched URL: {url}, item_id: {item_id}")
            else:
                print(f"[GUI DEBUG] No matching URL found for: {url}")
                return
        
        # Update stored information
        if status:
            video_info["status"] = status
        if progress is not None:
            video_info["progress"] = progress
        if title:
            video_info["title"] = title
        
        # Update the tree item
        try:
            current_values = list(self.videos_tree.item(item_id)["values"])
            print(f"[GUI DEBUG] Current tree values: {current_values}")
            
            # Update values for compact format (4 columns instead of 5)
            if title:
                current_values[1] = title[:40] + "..." if len(title) > 40 else title
            if status:
                current_values[2] = status
            if progress is not None:
                if isinstance(progress, (int, float)):
                    current_values[3] = f"{progress:.1f}%"
                else:
                    current_values[3] = str(progress)
            # Removed quality column for compact design
                
            print(f"[GUI DEBUG] New tree values: {current_values}")
            self.videos_tree.item(item_id, values=current_values)
            
            # Scroll to current item if it's being downloaded
            if status in ["Downloading", "Processing"]:
                self.videos_tree.see(item_id)
                
            print(f"[GUI DEBUG] Tree item updated successfully")
            
        except Exception as e:
            print(f"[GUI DEBUG ERROR] Failed to update tree item: {e}")
    
    def update_overall_progress(self):
        """Update overall progress based on individual video progress"""
        if not self.video_progress:
            return
            
        completed = sum(1 for v in self.video_progress.values() 
                       if v["status"] in ["Completed", "Failed"])
        total = len(self.video_progress)
        
        if total > 0:
            percentage = (completed / total) * 100
            self.overall_progress_bar["value"] = percentage
            
            # More concise progress display
            status_emoji = "✅" if completed == total else "⏳"
            self.overall_progress_var.set(f"{status_emoji} {completed}/{total} ({percentage:.0f}%)")
            
            print(f"[GUI DEBUG] Overall progress updated: {completed}/{total} = {percentage:.1f}%")
    
    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_var.set(folder)
    
    def clear_urls(self):
        """Clear the URLs text area"""
        self.urls_text.delete(1.0, tk.END)
    
    def log_message(self, message, color="black"):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_download(self):
        """Start the download process in a separate thread"""
        urls_text = self.urls_text.get(1.0, tk.END).strip()
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
        
        # Disable download button and enable stop button
        self.download_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Clear previous data
        self.log_text.delete(1.0, tk.END)
        self.clear_video_progress()
        self.download_stopped = False  # Reset the stop flag
        
        # Initialize progress tracking
        self.total_videos = len(urls)
        self.current_video_index = 0
        self.overall_progress_bar["maximum"] = 100
        self.overall_progress_bar["value"] = 0
        self.current_progress_bar["maximum"] = 100
        self.current_progress_bar["value"] = 0
        
        # Pre-populate video list
        for i, url in enumerate(urls, 1):
            self.add_video_to_progress(i, f"Video {i}", url)
        
        # Update overall progress
        self.overall_progress_var.set(f"Starting download of {len(urls)} URLs...")
        self.current_progress_var.set("Initializing...")
        
        # Start download thread
        self.download_thread = threading.Thread(
            target=self.download_worker, 
            args=(urls,), 
            daemon=True
        )
        self.download_thread.start()
    
    def run_ytdlp_with_tracking(self, ydl_opts, url):
        """Run yt-dlp download with process tracking for proper termination"""
        import yt_dlp
        
        # Store the original download method
        original_subprocess_run = subprocess.run
        
        def tracked_subprocess_run(*args, **kwargs):
            """Wrapper for subprocess.run to track processes"""
            try:
                # Create process with tracking
                kwargs['stdout'] = subprocess.PIPE
                kwargs['stderr'] = subprocess.PIPE
                process = subprocess.Popen(*args, **kwargs)
                
                # Add to our tracking list
                self.running_processes.append(process)
                print(f"[GUI DEBUG] Added process {process.pid} to tracking list")
                
                # Wait for completion and get results
                stdout, stderr = process.communicate()
                
                # Remove from tracking list when done
                if process in self.running_processes:
                    self.running_processes.remove(process)
                    print(f"[GUI DEBUG] Removed process {process.pid} from tracking list")
                
                # Create result object similar to subprocess.run
                class Result:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = stdout
                        self.stderr = stderr
                
                return Result(process.returncode, stdout, stderr)
                
            except Exception as e:
                print(f"[GUI DEBUG] Error in tracked subprocess: {e}")
                # Remove from tracking if there was an error
                if 'process' in locals() and process in self.running_processes:
                    self.running_processes.remove(process)
                raise
        
        # Monkey patch subprocess.run temporarily
        subprocess.run = tracked_subprocess_run
        
        try:
            # Run the download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
            return result
        finally:
            # Restore original subprocess.run
            subprocess.run = original_subprocess_run
    
    def download_worker(self, urls):
        """Worker function for downloading (runs in separate thread)"""
        try:
            import yt_dlp
            
            # Get selected format
            selected_format = self.get_selected_format()
            
            # Track current downloading URL
            self.current_downloading_url = None
            
            # Create a custom progress hook
            def progress_hook(d):
                try:
                    # Check if download was stopped
                    if self.download_stopped:
                        print(f"[DOWNLOAD DEBUG] Download stopped flag detected in progress hook")
                        # Terminate all processes when stop is detected
                        self.terminate_all_processes()
                        return
                    
                    print(f"[DOWNLOAD DEBUG] Progress hook called:")
                    print(f"  Status: {d.get('status')}")
                    print(f"  Filename: {d.get('filename', 'N/A')}")
                    print(f"  Downloaded: {d.get('downloaded_bytes', 0)}")
                    print(f"  Total: {d.get('total_bytes', 'N/A')}")
                    print(f"  Current downloading URL: {self.current_downloading_url}")
                    
                    if d['status'] == 'downloading':
                        # Extract progress information
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('total_bytes_estimate')
                        filename = d.get('filename', '')
                        
                        # Skip progress updates for audio fragments and subtitle files
                        if filename:
                            if '.srt' in filename or '.vtt' in filename:
                                print(f"[DOWNLOAD DEBUG] Subtitle download detected - skipping progress update")
                                return
                            elif any(f'.f{i}.' in filename for i in range(100, 999)) and ('.m4a' in filename or '.webm' in filename):
                                print(f"[DOWNLOAD DEBUG] Audio fragment download detected - skipping progress update")
                                return
                        
                        # Calculate progress - handle missing total bytes
                        if total and total > 0:
                            percent = (downloaded / total) * 100
                            print(f"[DOWNLOAD DEBUG] Calculated progress: {percent:.1f}% ({downloaded}/{total})")
                        else:
                            # For streams without total size, show activity
                            percent = 50  # Show 50% for unknown size video downloads
                            print(f"[DOWNLOAD DEBUG] Unknown size download - using 50% progress")
                            
                        speed = d.get('speed', 0)
                        eta = d.get('eta', 0)
                        
                        # Clean filename for display (handle both / and \ separators)
                        if filename:
                            display_filename = filename.replace('\\', '/').split('/')[-1]
                        else:
                            display_filename = 'Downloading...'
                        
                        # Update current video progress bar
                        progress_data = {
                            "percent": percent,
                            "speed": speed,
                            "eta": eta,
                            "filename": display_filename
                        }
                        print(f"[DOWNLOAD DEBUG] Sending current_progress message: {progress_data}")
                        self.message_queue.put(("current_progress", progress_data))
                        
                        # Update individual video progress if we have a current URL
                        if self.current_downloading_url:
                            video_progress_data = {
                                "url": self.current_downloading_url,
                                "progress": percent,
                                "status": "Downloading"
                            }
                            print(f"[DOWNLOAD DEBUG] Sending video_progress message: {video_progress_data}")
                            self.message_queue.put(("video_progress", video_progress_data))
                                
                    elif d['status'] == 'finished':
                        filename = d.get('filename', '')
                        print(f"[DOWNLOAD DEBUG] Download finished: {filename}")
                        
                        # Clean filename for display
                        if filename:
                            display_filename = filename.replace('\\', '/').split('/')[-1]
                        else:
                            display_filename = 'Processing...'
                        
                        # Only update video progress to "Processing" for main video files, not subtitles or audio fragments
                        if self.current_downloading_url:
                            if '.srt' in filename or '.vtt' in filename:
                                print(f"[DOWNLOAD DEBUG] Subtitle finished - not updating video status")
                                # Don't update progress for subtitles
                            elif '.m4a' in filename or '.webm' in filename or '.mp3' in filename:
                                print(f"[DOWNLOAD DEBUG] Audio track finished - not updating video status")
                                # Don't update progress for audio tracks during merging
                            elif any(f'.f{i}.' in filename for i in range(100, 999)):
                                print(f"[DOWNLOAD DEBUG] Video/Audio fragment finished - not updating video status")
                                # Don't update progress for individual fragments during merging
                            else:
                                print(f"[DOWNLOAD DEBUG] Main video finished - updating to Processing")
                                self.message_queue.put(("video_progress", {
                                    "url": self.current_downloading_url,
                                    "progress": 100,
                                    "status": "Processing"
                                }))
                                
                                # Update current progress to show processing
                                self.message_queue.put(("current_progress", {
                                    "percent": 100,
                                    "speed": 0,
                                    "eta": 0,
                                    "filename": "Processing..."
                                }))
                            
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG ERROR] Progress hook error: {e}")
                    self.message_queue.put(("log", f"Progress hook error: {e}"))
            
            # Process each URL
            results = {}
            for i, url in enumerate(urls, 1):
                # Check if download was stopped
                if self.download_stopped:
                    print(f"[DOWNLOAD DEBUG] Download stopped by user")
                    self.message_queue.put(("error", "Download was stopped by user"))
                    return
                
                print(f"\n[DOWNLOAD DEBUG] ===== Processing URL {i}/{len(urls)} =====")
                print(f"[DOWNLOAD DEBUG] URL: {url}")
                
                self.current_video_index = i
                self.current_downloading_url = url
                
                self.message_queue.put(("overall_progress", f"Processing {i}/{len(urls)}: Extracting info..."))
                
                try:
                    # Update video status to extracting info
                    print(f"[DOWNLOAD DEBUG] Sending extracting info status for: {url}")
                    self.message_queue.put(("video_progress", {
                        "url": url,
                        "status": "Extracting info...",
                        "progress": 0
                    }))
                    
                    # First, extract video info to get title and quality info
                    print(f"[DOWNLOAD DEBUG] Extracting video info...")
                    ydl_opts_info = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': False,
                        'ignoreerrors': True,  # Continue processing even if some videos fail
                        'skip_unavailable_fragments': True,  # Skip unavailable content
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(url, download=False)
                        print(f"[DOWNLOAD DEBUG] Info extracted successfully")
                        
                        if 'entries' in info:  # Playlist
                            print(f"[DOWNLOAD DEBUG] Detected playlist")
                            # Handle playlist
                            playlist_title = info.get('title', f'Playlist {i}')
                            entries = [e for e in info['entries'] if e is not None]
                            
                            # Filter out None entries and private/unavailable videos
                            available_entries = []
                            unavailable_count = 0
                            for entry in info['entries']:
                                if entry is None:
                                    unavailable_count += 1
                                else:
                                    available_entries.append(entry)
                            
                            total_entries = len(info['entries'])
                            print(f"[DOWNLOAD DEBUG] Playlist: {playlist_title}")
                            print(f"[DOWNLOAD DEBUG] Total entries: {total_entries}, Available: {len(available_entries)}, Unavailable: {unavailable_count}")
                            
                            if unavailable_count > 0:
                                self.message_queue.put(("log", f"Found playlist: {playlist_title} with {total_entries} videos ({unavailable_count} private/unavailable)"))
                            else:
                                self.message_queue.put(("log", f"Found playlist: {playlist_title} with {len(available_entries)} videos"))
                            
                            # Update the main playlist entry
                            playlist_status = f"{len(available_entries)} videos"
                            if unavailable_count > 0:
                                playlist_status += f" ({unavailable_count} private/unavailable)"
                            
                            self.message_queue.put(("video_progress", {
                                "url": url,
                                "title": f"📂 {playlist_title}",
                                "status": "Processing playlist",
                                "progress": 0,
                                "quality": playlist_status
                            }))
                            
                            # Process each video in the playlist
                            playlist_success = 0
                            playlist_failed = 0
                            processed_videos = set()  # Track processed videos to avoid duplicates
                            for j, entry in enumerate(available_entries):
                                # Check if download was stopped
                                if self.download_stopped:
                                    print(f"[DOWNLOAD DEBUG] Playlist download stopped by user")
                                    break
                                
                                if entry:
                                    video_title = entry.get('title', f'Video {j+1}')
                                    video_url = entry.get('webpage_url') or entry.get('url', f'{url}#{j}')
                                    
                                    # Skip if already processed
                                    if video_url in processed_videos:
                                        print(f"[DOWNLOAD DEBUG] Skipping duplicate video: {video_url}")
                                        continue
                                    processed_videos.add(video_url)
                                    
                                    # Add to tracking - notify GUI about the new video
                                    self.message_queue.put(("add_playlist_video", {
                                        "index": f"{i}.{j+1}",
                                        "title": f"  └ {video_title}",
                                        "url": video_url
                                    }))
                                    
                                    # Download individual video
                                    self.current_downloading_url = video_url
                                    
                                    try:
                                        self.message_queue.put(("video_progress", {
                                            "url": video_url,
                                            "status": "Downloading",
                                            "progress": 0
                                        }))
                                        
                                        # Download with progress tracking - Enhanced quality options
                                        ydl_opts = {
                                            'format': selected_format,
                                            'outtmpl': str(Path(self.download_path) / 'Playlists' / f'{playlist_title}' / f'{j+1:02d} - %(title)s.%(ext)s'),
                                            'restrictfilenames': True,
                                            'writesubtitles': self.download_subtitles_var.get(),
                                            'writeautomaticsub': self.download_subtitles_var.get(),
                                            'subtitleslangs': ['en', 'en-US', 'en-GB', 'en.*'],
                                            'subtitlesformat': 'srt/vtt/best',
                                            'embedsubs': self.embed_subtitles_var.get(),
                                            'ignoreerrors': True,
                                            'no_warnings': True,
                                            'progress_hooks': [progress_hook],
                                            'retries': 3,
                                            'fragment_retries': 3,
                                            'extractor_retries': 3,
                                            # Enhanced quality and merging options
                                            'merge_output_format': 'mp4',  # Ensure output is MP4
                                            'postprocessors': [
                                                {
                                                    'key': 'FFmpegVideoConvertor',
                                                    'preferedformat': 'mp4',
                                                },
                                                {
                                                    'key': 'FFmpegMetadata',
                                                    'add_metadata': True,
                                                }
                                            ],
                                            'prefer_ffmpeg': True,  # Use ffmpeg for better quality
                                            'keepvideo': False,  # Remove source files after merge
                                            'writeinfojson': False,  # Don't write info files
                                            'writethumbnail': False,  # Don't write thumbnail files
                                        }
                                        
                                        # Use tracked download method
                                        self.run_ytdlp_with_tracking(ydl_opts, video_url)
                                            
                                        playlist_success += 1
                                        
                                        # Ensure the video is marked as completed
                                        print(f"[DOWNLOAD DEBUG] Playlist video {j+1} download completed successfully")
                                        self.message_queue.put(("video_progress", {
                                            "url": video_url,
                                            "status": "Completed",
                                            "progress": 100
                                        }))
                                        
                                    except Exception as video_error:
                                        playlist_failed += 1
                                        error_msg = str(video_error)
                                        
                                        # Provide user-friendly error messages
                                        if "Private video" in error_msg:
                                            friendly_error = "Private/Restricted"
                                        elif "Video unavailable" in error_msg:
                                            friendly_error = "Unavailable"
                                        elif "Sign in" in error_msg:
                                            friendly_error = "Login Required"
                                        else:
                                            friendly_error = "Failed"
                                        
                                        self.message_queue.put(("video_progress", {
                                            "url": video_url,
                                            "status": friendly_error,
                                            "progress": 0
                                        }))
                                        self.message_queue.put(("log", f"⚠️  Playlist video {j+1} ({video_title[:30]}...): {friendly_error}"))
                                    
                                    # Update playlist progress
                                    playlist_progress = ((j + 1) / len(available_entries)) * 100
                                    self.message_queue.put(("video_progress", {
                                        "url": url,
                                        "progress": playlist_progress,
                                        "status": f"Processing ({j+1}/{len(available_entries)})"
                                    }))
                            
                            # Final playlist status
                            total_processed = playlist_success + playlist_failed
                            if playlist_success == len(available_entries):
                                self.message_queue.put(("video_progress", {
                                    "url": url,
                                    "status": "Completed",
                                    "progress": 100
                                }))
                                results[url] = True
                            elif playlist_success > 0:
                                status_text = f"Partial ({playlist_success}/{len(available_entries)})"
                                if unavailable_count > 0:
                                    status_text += f" +{unavailable_count} unavailable"
                                self.message_queue.put(("video_progress", {
                                    "url": url,
                                    "status": status_text,
                                    "progress": 100
                                }))
                                results[url] = True  # Consider partial success as success
                            else:
                                status_text = "Failed"
                                if unavailable_count > 0:
                                    status_text += f" ({unavailable_count} unavailable)"
                                self.message_queue.put(("video_progress", {
                                    "url": url,
                                    "status": status_text,
                                    "progress": 100
                                }))
                                results[url] = False
                            
                            # Log summary
                            if playlist_success > 0:
                                self.message_queue.put(("log", f"✓ Playlist completed: {playlist_success} successful, {playlist_failed} failed"))
                            else:
                                self.message_queue.put(("log", f"✗ Playlist failed: No videos could be downloaded"))
                                
                        else:  # Single video
                            print(f"[DOWNLOAD DEBUG] Detected single video")
                            video_title = info.get('title', f'Video {i}')
                            formats = info.get('formats', [])
                            
                            print(f"[DOWNLOAD DEBUG] Video title: {video_title}")
                            print(f"[DOWNLOAD DEBUG] Available formats: {len(formats)}")
                            
                            # Find quality info - Enhanced to show more details
                            quality_info = "Unknown"
                            best_height = 0
                            best_fps = 0
                            video_codec = "Unknown"
                            audio_codec = "Unknown"
                            
                            for fmt in formats:
                                height = fmt.get('height', 0)
                                fps = fmt.get('fps', 0) or 30
                                vcodec = fmt.get('vcodec', 'none')
                                acodec = fmt.get('acodec', 'none')
                                
                                if height and height > best_height:
                                    best_height = height
                                    best_fps = fps
                                    if vcodec != 'none':
                                        video_codec = vcodec
                                    if acodec != 'none':
                                        audio_codec = acodec
                            
                            if best_height > 0:
                                quality_info = f"{best_height}p"
                                if best_fps > 30:
                                    quality_info += f"@{best_fps}fps"
                                if video_codec != "Unknown" and "vp9" in video_codec.lower():
                                    quality_info += " (VP9)"
                                elif video_codec != "Unknown" and "avc1" in video_codec.lower():
                                    quality_info += " (H.264)"
                            
                            print(f"[DOWNLOAD DEBUG] Best quality: {quality_info}")
                            print(f"[DOWNLOAD DEBUG] Video codec: {video_codec}, Audio codec: {audio_codec}")
                            
                            # Update video info with title and quality
                            video_update_data = {
                                "url": url,
                                "title": video_title,
                                "status": "Ready to download",
                                "quality": quality_info,
                                "progress": 0
                            }
                            print(f"[DOWNLOAD DEBUG] Sending video update: {video_update_data}")
                            self.message_queue.put(("video_progress", video_update_data))
                    
                    # For single videos, download now
                    if 'entries' not in info:
                        print(f"[DOWNLOAD DEBUG] Starting single video download")
                        # Download with progress tracking - Enhanced quality options
                        ydl_opts = {
                            'format': selected_format,
                            'outtmpl': str(Path(self.download_path) / 'Single Videos' / '%(title)s.%(ext)s'),
                            'restrictfilenames': True,
                            'writesubtitles': self.download_subtitles_var.get(),
                            'writeautomaticsub': self.download_subtitles_var.get(),
                            'subtitleslangs': ['en', 'en-US', 'en-GB', 'en.*'],
                            'subtitlesformat': 'srt/vtt/best',
                            'embedsubs': self.embed_subtitles_var.get(),
                            'ignoreerrors': True,
                            'no_warnings': True,
                            'progress_hooks': [progress_hook],
                            'retries': 3,
                            'fragment_retries': 3,
                            'extractor_retries': 3,
                            # Enhanced quality and merging options
                            'merge_output_format': 'mp4',  # Ensure output is MP4
                            'postprocessors': [
                                {
                                    'key': 'FFmpegVideoConvertor',
                                    'preferedformat': 'mp4',
                                },
                                {
                                    'key': 'FFmpegMetadata',
                                    'add_metadata': True,
                                }
                            ],
                            'prefer_ffmpeg': True,  # Use ffmpeg for better quality
                            'keepvideo': False,  # Remove source files after merge
                            'writeinfojson': False,  # Don't write info files
                            'writethumbnail': False,  # Don't write thumbnail files
                        }
                        
                        # Update status to downloading
                        print(f"[DOWNLOAD DEBUG] Setting status to downloading for: {url}")
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Downloading",
                            "progress": 0
                        }))
                        
                        print(f"[DOWNLOAD DEBUG] Starting yt-dlp download...")
                        # Use tracked download method
                        self.run_ytdlp_with_tracking(ydl_opts, url)
                        print(f"[DOWNLOAD DEBUG] yt-dlp download completed")
                            
                        results[url] = True
                        
                        # Update video status to completed
                        print(f"[DOWNLOAD DEBUG] Setting status to completed for: {url}")
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Completed",
                            "progress": 100
                        }))
                        
                        # Also update current progress to show completion
                        self.message_queue.put(("current_progress", {
                            "percent": 100,
                            "speed": 0,
                            "eta": 0,
                            "filename": "Complete"
                        }))
                        
                        self.message_queue.put(("log", f"✓ [{i}/{len(urls)}] Completed: {video_title}"))
                    
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG ERROR] Exception occurred: {e}")
                    results[url] = False
                    error_msg = str(e)
                    
                    # Provide user-friendly error messages
                    if "Private video" in error_msg:
                        friendly_error = "❌ Private/Restricted content - Authentication required"
                        status = "Private/Restricted"
                    elif "Video unavailable" in error_msg:
                        friendly_error = "❌ Video unavailable or deleted"
                        status = "Unavailable"
                    elif "Sign in" in error_msg:
                        friendly_error = "❌ Login required for this content"
                        status = "Login Required"
                    elif "cookies" in error_msg.lower():
                        friendly_error = "❌ Authentication required (cookies needed)"
                        status = "Auth Required"
                    elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                        friendly_error = "❌ Network connection error"
                        status = "Network Error"
                    else:
                        friendly_error = f"❌ Download failed: {error_msg[:100]}..."
                        status = "Failed"
                    
                    # Update video status to failed
                    self.message_queue.put(("video_progress", {
                        "url": url,
                        "status": status,
                        "progress": 0
                    }))
                    
                    self.message_queue.put(("log", f"✗ [{i}/{len(urls)}] {friendly_error}"))
                
                # Update overall progress
                print(f"[DOWNLOAD DEBUG] Updating overall progress")
                self.message_queue.put(("update_overall", None))
            
            # Send completion message
            successful = sum(1 for success in results.values() if success)
            failed = len(urls) - successful
            
            print(f"[DOWNLOAD DEBUG] ===== DOWNLOAD COMPLETE =====")
            print(f"[DOWNLOAD DEBUG] Successful: {successful}")
            print(f"[DOWNLOAD DEBUG] Failed: {failed}")
            print(f"[DOWNLOAD DEBUG] Total: {len(urls)}")
            
            # Final overall progress update
            self.message_queue.put(("overall_progress", f"Finalizing... {successful}/{len(urls)} completed"))
            
            self.message_queue.put(("complete", {
                "successful": successful,
                "failed": failed,
                "total": len(urls)
            }))
            
        except KeyboardInterrupt:
            print(f"[DOWNLOAD DEBUG] Download interrupted by user")
            self.message_queue.put(("error", "Download was interrupted by user"))
        except Exception as e:
            print(f"[DOWNLOAD DEBUG CRITICAL ERROR] {e}")
            import traceback
            traceback.print_exc()
            self.message_queue.put(("error", f"Download error: {e}"))
    
    def stop_download(self):
        """Stop the download process"""
        print("[GUI DEBUG] Stop download requested")
        self.download_stopped = True
        self.overall_progress_bar.stop()
        self.current_progress_bar.stop()
        self.overall_progress_var.set("Stopping download...")
        self.current_progress_var.set("Stopping...")
        self.log_message("Stopping download...", "orange")
        
        # Terminate all running processes
        self.terminate_all_processes()
        
        # Wait for thread to finish gracefully (with timeout)
        if hasattr(self, 'download_thread') and self.download_thread and self.download_thread.is_alive():
            print("[GUI DEBUG] Waiting for download thread to finish...")
            self.download_thread.join(timeout=3.0)  # Wait up to 3 seconds
            
            if self.download_thread.is_alive():
                print("[GUI DEBUG] Download thread still running after timeout")
                # Force thread termination if needed (not recommended but as last resort)
        
        # Update UI
        self.overall_progress_var.set("Download stopped")
        self.current_progress_var.set("Stopped")
        self.download_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("Download stopped by user", "red")
        print("[GUI DEBUG] Download stop completed")
    
    def terminate_all_processes(self):
        """Terminate all running yt-dlp processes"""
        try:
            print(f"[GUI DEBUG] Terminating {len(self.running_processes)} processes...")
            
            # First, try to terminate processes gracefully
            for proc in self.running_processes[:]:  # Create a copy to iterate
                try:
                    if proc.poll() is None:  # Process is still running
                        print(f"[GUI DEBUG] Terminating process PID: {proc.pid}")
                        proc.terminate()
                except Exception as e:
                    print(f"[GUI DEBUG] Error terminating process: {e}")
            
            # Wait a moment for graceful termination
            import time
            time.sleep(1)
            
            # Force kill any remaining processes
            for proc in self.running_processes[:]:
                try:
                    if proc.poll() is None:  # Still running
                        print(f"[GUI DEBUG] Force killing process PID: {proc.pid}")
                        proc.kill()
                        proc.wait(timeout=1)
                except Exception as e:
                    print(f"[GUI DEBUG] Error force killing process: {e}")
            
            # Clear the process list
            self.running_processes.clear()
            
            # Additionally, try to kill any yt-dlp processes that might be running
            if PSUTIL_AVAILABLE:
                try:
                    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            cmdline = process.info['cmdline']
                            if cmdline and any('yt-dlp' in str(arg) for arg in cmdline):
                                print(f"[GUI DEBUG] Found and terminating yt-dlp process: {process.info['pid']}")
                                psutil.Process(process.info['pid']).terminate()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    print(f"[GUI DEBUG] Error searching for yt-dlp processes: {e}")
            else:
                print("[GUI DEBUG] psutil not available, cannot search for additional yt-dlp processes")
                
        except Exception as e:
            print(f"[GUI DEBUG] Error in terminate_all_processes: {e}")
            self.running_processes.clear()  # Clear the list anyway
    
    def update_messages(self):
        """Process messages from download thread"""
        try:
            message_count = 0
            while True:
                message_type, data = self.message_queue.get_nowait()
                message_count += 1
                
                print(f"[GUI DEBUG] Processing message {message_count}: {message_type}")
                if isinstance(data, dict):
                    print(f"[GUI DEBUG] Message data: {data}")
                else:
                    print(f"[GUI DEBUG] Message data: {str(data)[:100]}")
                
                if message_type == "log":
                    self.log_message(data)
                elif message_type == "overall_progress":
                    print(f"[GUI DEBUG] Updating overall progress: {data}")
                    self.overall_progress_var.set(data)
                elif message_type == "current_progress":
                    percent = data.get("percent", 0)
                    speed = data.get("speed", 0)
                    eta = data.get("eta", 0)
                    filename = data.get("filename", "")
                    
                    print(f"[GUI DEBUG] Updating current progress: {percent:.1f}%")
                    self.current_progress_bar["value"] = percent
                    
                    speed_text = ""
                    if speed is not None and speed > 0:
                        if speed > 1024*1024:
                            speed_text = f" at {speed/(1024*1024):.1f} MB/s"
                        elif speed > 1024:
                            speed_text = f" at {speed/1024:.1f} KB/s"
                        else:
                            speed_text = f" at {speed:.0f} B/s"
                    
                    eta_text = ""
                    if eta is not None and eta > 0:
                        eta_text = f" (ETA: {eta//60}:{eta%60:02d})"
                    
                    progress_text = f"Downloading: {percent:.1f}%{speed_text}{eta_text}"
                    print(f"[GUI DEBUG] Setting current progress text: {progress_text}")
                    self.current_progress_var.set(progress_text)
                elif message_type == "video_progress":
                    url = data["url"]
                    status = data.get("status")
                    progress = data.get("progress")
                    quality = data.get("quality")
                    title = data.get("title")
                    
                    print(f"[GUI DEBUG] Received video_progress message for URL: {url}")
                    self.update_video_progress(url, status, progress, quality, title)
                elif message_type == "add_playlist_video":
                    index = data["index"]
                    title = data["title"]
                    url = data["url"]
                    print(f"[GUI DEBUG] Adding playlist video: {index} - {title}")
                    self.add_video_to_progress(index, title, url)
                elif message_type == "update_overall":
                    print(f"[GUI DEBUG] Updating overall progress bar")
                    self.update_overall_progress()
                elif message_type == "complete":
                    print(f"[GUI DEBUG] Download complete message received")
                    self.overall_progress_bar.stop()
                    self.current_progress_bar["value"] = 0
                    self.current_progress_var.set("Complete")
                    
                    self.overall_progress_var.set(
                        f"Complete! {data['successful']}/{data['total']} successful"
                    )
                    self.download_button.config(state="normal")
                    self.stop_button.config(state="disabled")
                    
                    # Show completion message
                    if data['failed'] > 0:
                        # Check if we have authentication-related failures
                        auth_issues = any(
                            video["status"] in ["Private/Restricted", "Login Required", "Auth Required"]
                            for video in self.video_progress.values()
                        )
                        
                        failure_msg = (
                            f"Download completed with some issues:\n"
                            f"✅ Successful: {data['successful']}\n"
                            f"❌ Failed: {data['failed']}\n\n"
                            f"Check the log and individual video status for details."
                        )
                        
                        if auth_issues:
                            failure_msg += (
                                f"\n\n💡 Tip: Some videos are private or require login. "
                                f"For private playlists, make sure you're logged into YouTube "
                                f"in your browser and the playlist is public or you have access."
                            )
                        
                        messagebox.showwarning("Download Complete", failure_msg)
                    else:
                        messagebox.showinfo(
                            "Download Complete",
                            f"🎉 All {data['successful']} downloads completed successfully!"
                        )
                elif message_type == "error":
                    print(f"[GUI DEBUG] Error message received: {data}")
                    self.overall_progress_bar.stop()
                    self.current_progress_bar.stop()
                    self.overall_progress_var.set("Error occurred")
                    self.current_progress_var.set("Error")
                    self.download_button.config(state="normal")
                    self.stop_button.config(state="disabled")
                    self.log_message(f"ERROR: {data}", "red")
                    messagebox.showerror("Download Error", data)
                else:
                    print(f"[GUI DEBUG] Unknown message type: {message_type}")
                    
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_messages)
    
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
