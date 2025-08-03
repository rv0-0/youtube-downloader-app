"""
GUI version of the YouTube Downloader using tkinter
Enhanced with quality selection and individual video progress tracking
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import sys
import time
from pathlib import Path

# Import our YouTube downloader
from youtube_downloader import YouTubeDownloader


class YouTubeDownloaderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader - Enhanced")
        self.root.geometry("900x700")
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Downloader instance
        self.downloader = None
        self.download_path = "Downloads"
        
        # Video progress tracking
        self.video_progress = {}
        self.current_video_index = 0
        self.total_videos = 0
        
        # Quality options
        self.quality_options = {
            "Best Quality (4K/1440p/1080p)": "best",
            "High Quality (1080p max)": "best[height<=1080]",
            "Medium Quality (720p max)": "best[height<=720]", 
            "Low Quality (480p max)": "best[height<=480]",
            "Audio Only (Best)": "bestaudio/best",
            "Custom Format": "custom"
        }
        
        self.setup_ui()
        self.update_messages()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame with scrollable content
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎬 YouTube Downloader - Enhanced", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Download path selection
        path_frame = ttk.LabelFrame(main_frame, text="Download Location", padding="5")
        path_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar(value=self.download_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_folder)
        browse_button.grid(row=0, column=2, sticky=tk.W)
        
        # Quality selection
        quality_frame = ttk.LabelFrame(main_frame, text="Video Quality", padding="5")
        quality_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        quality_frame.columnconfigure(1, weight=1)
        
        ttk.Label(quality_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="High Quality (1080p max)")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                   values=list(self.quality_options.keys()), 
                                   state="readonly", width=30)
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 5))
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)
        
        # Custom format entry (initially hidden)
        self.custom_format_frame = ttk.Frame(quality_frame)
        self.custom_format_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.custom_format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.custom_format_frame, text="Custom Format:").grid(row=0, column=0, sticky=tk.W)
        self.custom_format_var = tk.StringVar(value="best[height<=1080]/best")
        self.custom_format_entry = ttk.Entry(self.custom_format_frame, textvariable=self.custom_format_var)
        self.custom_format_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        help_button = ttk.Button(self.custom_format_frame, text="?", width=3, 
                               command=self.show_format_help)
        help_button.grid(row=0, column=2, sticky=tk.W)
        
        # Hide custom format initially
        self.custom_format_frame.grid_remove()
        
        # Subtitle options
        subtitle_frame = ttk.LabelFrame(main_frame, text="Subtitle Options", padding="5")
        subtitle_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        subtitle_frame.columnconfigure(1, weight=1)
        
        self.download_subtitles_var = tk.BooleanVar(value=True)
        subtitle_check = ttk.Checkbutton(subtitle_frame, text="Download English subtitles", 
                                        variable=self.download_subtitles_var)
        subtitle_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.embed_subtitles_var = tk.BooleanVar(value=False)
        embed_check = ttk.Checkbutton(subtitle_frame, text="Embed subtitles in video", 
                                     variable=self.embed_subtitles_var)
        embed_check.grid(row=0, column=1, sticky=tk.W)
        
        # URLs input
        urls_frame = ttk.LabelFrame(main_frame, text="YouTube URLs", padding="5")
        urls_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        urls_frame.columnconfigure(0, weight=1)
        urls_frame.rowconfigure(1, weight=1)
        
        ttk.Label(urls_frame, text="Enter YouTube URLs (one per line):").grid(row=0, column=0, sticky=tk.W)
        
        self.urls_text = scrolledtext.ScrolledText(urls_frame, height=6, width=60)
        self.urls_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        self.download_button = ttk.Button(buttons_frame, text="Start Download", 
                                         command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ttk.Button(buttons_frame, text="Clear URLs", 
                                 command=self.clear_urls)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", 
                                     command=self.stop_download, state="disabled")
        self.stop_button.pack(side=tk.LEFT)
        
        # Overall Progress frame
        overall_progress_frame = ttk.LabelFrame(main_frame, text="Overall Progress", padding="5")
        overall_progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        overall_progress_frame.columnconfigure(0, weight=1)
        
        self.overall_progress_var = tk.StringVar(value="Ready")
        overall_progress_label = ttk.Label(overall_progress_frame, textvariable=self.overall_progress_var)
        overall_progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.overall_progress_bar = ttk.Progressbar(overall_progress_frame, mode='determinate')
        self.overall_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Current Video Progress frame
        current_progress_frame = ttk.LabelFrame(main_frame, text="Current Video Progress", padding="5")
        current_progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        current_progress_frame.columnconfigure(0, weight=1)
        
        self.current_progress_var = tk.StringVar(value="No active download")
        current_progress_label = ttk.Label(current_progress_frame, textvariable=self.current_progress_var)
        current_progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.current_progress_bar = ttk.Progressbar(current_progress_frame, mode='determinate')
        self.current_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Individual Videos Progress frame
        videos_progress_frame = ttk.LabelFrame(main_frame, text="Individual Videos", padding="5")
        videos_progress_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        videos_progress_frame.columnconfigure(0, weight=1)
        videos_progress_frame.rowconfigure(0, weight=1)
        
        # Create treeview for video progress
        columns = ("Index", "Title", "Status", "Progress", "Quality")
        self.videos_tree = ttk.Treeview(videos_progress_frame, columns=columns, show="headings", height=8)
        
        # Configure column headings
        self.videos_tree.heading("Index", text="#")
        self.videos_tree.heading("Title", text="Video Title")
        self.videos_tree.heading("Status", text="Status")
        self.videos_tree.heading("Progress", text="Progress")
        self.videos_tree.heading("Quality", text="Quality")
        
        # Configure column widths
        self.videos_tree.column("Index", width=50, anchor="center")
        self.videos_tree.column("Title", width=300)
        self.videos_tree.column("Status", width=100, anchor="center")
        self.videos_tree.column("Progress", width=100, anchor="center")
        self.videos_tree.column("Quality", width=120, anchor="center")
        
        # Add scrollbars for treeview
        tree_scrollbar_y = ttk.Scrollbar(videos_progress_frame, orient="vertical", command=self.videos_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(videos_progress_frame, orient="horizontal", command=self.videos_tree.xview)
        self.videos_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        self.videos_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Download Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure row weights for proper expansion
        main_frame.rowconfigure(8, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def on_quality_change(self, event=None):
        """Handle quality selection change"""
        if self.quality_var.get() == "Custom Format":
            self.custom_format_frame.grid()
        else:
            self.custom_format_frame.grid_remove()
    
    def show_format_help(self):
        """Show help dialog for custom format"""
        help_text = """Custom Format Examples:
        
• best - Best quality available
• best[height<=1080] - Best up to 1080p
• best[height<=720] - Best up to 720p
• worst - Lowest quality
• bestaudio - Audio only
• best[ext=mp4] - Best MP4 format
• best[vcodec^=avc1] - Best H.264 format
• bestvideo+bestaudio - Merge best video and audio

See yt-dlp documentation for more format options."""
        
        messagebox.showinfo("Format Help", help_text)
    
    def get_selected_format(self):
        """Get the currently selected video format"""
        quality_name = self.quality_var.get()
        if quality_name == "Custom Format":
            return self.custom_format_var.get()
        else:
            return self.quality_options.get(quality_name, "best[height<=1080]")
    
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
        
        # For playlist videos, don't use the total_videos in the display index
        # as it may not be updated yet when playlist videos are being added
        display_index = str(index) if isinstance(index, str) else f"{index}"
        
        item_id = self.videos_tree.insert("", "end", values=(
            display_index,
            title[:50] + "..." if len(title) > 50 else title,
            "Pending",
            "0%",
            "Detecting..."
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
            print(f"[GUI DEBUG] Available URLs in tracking:")
            
            matched_url = None
            for i, key in enumerate(self.video_progress.keys()):
                print(f"  {i+1}: {key}")
                # Try to match by video ID (extract from URL)
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
            
            # Update values
            if title:
                current_values[1] = title[:50] + "..." if len(title) > 50 else title
            if status:
                current_values[2] = status
            if progress is not None:
                if isinstance(progress, (int, float)):
                    current_values[3] = f"{progress:.1f}%"
                else:
                    current_values[3] = str(progress)
            if quality:
                current_values[4] = quality
                
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
            self.overall_progress_var.set(f"Overall: {completed}/{total} videos completed ({percentage:.1f}%)")
            
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
                        
                        # Calculate progress - handle missing total bytes
                        if total and total > 0:
                            percent = (downloaded / total) * 100
                            print(f"[DOWNLOAD DEBUG] Calculated progress: {percent:.1f}% ({downloaded}/{total})")
                        else:
                            # For subtitle files and streams without total size, show activity
                            if '.srt' in filename or '.vtt' in filename:
                                percent = 75  # Show 75% for subtitle downloads to indicate activity
                                print(f"[DOWNLOAD DEBUG] Subtitle download detected - using 75% progress")
                            else:
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
                        
                        self.message_queue.put(("current_progress", {
                            "percent": 100,
                            "speed": 0,
                            "eta": 0,
                            "filename": display_filename
                        }))
                        
                        # Only update video progress to "Processing" for main video files, not subtitles
                        if self.current_downloading_url:
                            if '.srt' in filename or '.vtt' in filename:
                                print(f"[DOWNLOAD DEBUG] Subtitle finished - not updating video status")
                            else:
                                print(f"[DOWNLOAD DEBUG] Main video finished - updating to Processing")
                                self.message_queue.put(("video_progress", {
                                    "url": self.current_downloading_url,
                                    "progress": 100,
                                    "status": "Processing"
                                }))
                                
                                # Also update the current progress to show completion
                                self.message_queue.put(("current_progress", {
                                    "percent": 100,
                                    "speed": 0,
                                    "eta": 0,
                                    "filename": "Complete"
                                }))
                            
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG ERROR] Progress hook error: {e}")
                    self.message_queue.put(("log", f"Progress hook error: {e}"))
            
            # Process each URL
            results = {}
            for i, url in enumerate(urls, 1):
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
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(url, download=False)
                        print(f"[DOWNLOAD DEBUG] Info extracted successfully")
                        
                        if 'entries' in info:  # Playlist
                            print(f"[DOWNLOAD DEBUG] Detected playlist")
                            # Handle playlist
                            playlist_title = info.get('title', f'Playlist {i}')
                            entries = [e for e in info['entries'] if e is not None]
                            
                            print(f"[DOWNLOAD DEBUG] Playlist: {playlist_title}, {len(entries)} videos")
                            self.message_queue.put(("log", f"Found playlist: {playlist_title} with {len(entries)} videos"))
                            
                            # Update the main playlist entry
                            self.message_queue.put(("video_progress", {
                                "url": url,
                                "title": f"📂 {playlist_title}",
                                "status": "Processing playlist",
                                "progress": 0,
                                "quality": f"{len(entries)} videos"
                            }))
                            
                            # Process each video in the playlist
                            playlist_success = 0
                            for j, entry in enumerate(entries):
                                if entry:
                                    video_title = entry.get('title', f'Video {j+1}')
                                    video_url = entry.get('webpage_url') or entry.get('url', f'{url}#{j}')
                                    
                                    # Add to tracking - notify GUI about the new total
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
                                        
                                        # Download with progress tracking
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
                                        }
                                        
                                        with yt_dlp.YoutubeDL(ydl_opts) as ydl_playlist:
                                            ydl_playlist.download([video_url])
                                            
                                        playlist_success += 1
                                        
                                        # Ensure the video is marked as completed
                                        print(f"[DOWNLOAD DEBUG] Playlist video {j+1} download completed successfully")
                                        self.message_queue.put(("video_progress", {
                                            "url": video_url,
                                            "status": "Completed",
                                            "progress": 100
                                        }))
                                        
                                    except Exception as video_error:
                                        self.message_queue.put(("video_progress", {
                                            "url": video_url,
                                            "status": "Failed",
                                            "progress": 0
                                        }))
                                        self.message_queue.put(("log", f"Failed to download playlist video {j+1}: {video_error}"))
                                    
                                    # Update playlist progress
                                    playlist_progress = ((j + 1) / len(entries)) * 100
                                    self.message_queue.put(("video_progress", {
                                        "url": url,
                                        "progress": playlist_progress,
                                        "status": f"Processing ({j+1}/{len(entries)})"
                                    }))
                            
                            # Final playlist status
                            if playlist_success == len(entries):
                                self.message_queue.put(("video_progress", {
                                    "url": url,
                                    "status": "Completed",
                                    "progress": 100
                                }))
                                results[url] = True
                            else:
                                self.message_queue.put(("video_progress", {
                                    "url": url,
                                    "status": f"Partial ({playlist_success}/{len(entries)})",
                                    "progress": 100
                                }))
                                results[url] = playlist_success > 0
                                
                        else:  # Single video
                            print(f"[DOWNLOAD DEBUG] Detected single video")
                            video_title = info.get('title', f'Video {i}')
                            formats = info.get('formats', [])
                            
                            print(f"[DOWNLOAD DEBUG] Video title: {video_title}")
                            print(f"[DOWNLOAD DEBUG] Available formats: {len(formats)}")
                            
                            # Find quality info
                            quality_info = "Unknown"
                            best_height = 0
                            for fmt in formats:
                                height = fmt.get('height', 0)
                                if height and height > best_height:
                                    best_height = height
                                    quality_info = f"{height}p"
                            
                            print(f"[DOWNLOAD DEBUG] Best quality: {quality_info}")
                            
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
                        # Download with progress tracking
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
                        }
                        
                        # Update status to downloading
                        print(f"[DOWNLOAD DEBUG] Setting status to downloading for: {url}")
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Downloading",
                            "progress": 0
                        }))
                        
                        print(f"[DOWNLOAD DEBUG] Starting yt-dlp download...")
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        print(f"[DOWNLOAD DEBUG] yt-dlp download completed")
                            
                        results[url] = True
                        
                        # Update video status to completed
                        print(f"[DOWNLOAD DEBUG] Setting status to completed for: {url}")
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Completed",
                            "progress": 100
                        }))
                        
                        self.message_queue.put(("log", f"✓ [{i}/{len(urls)}] Completed: {video_title}"))
                    
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG ERROR] Exception occurred: {e}")
                    results[url] = False
                    error_msg = str(e)
                    
                    # Update video status to failed
                    self.message_queue.put(("video_progress", {
                        "url": url,
                        "status": "Failed",
                        "progress": 0
                    }))
                    
                    self.message_queue.put(("log", f"✗ [{i}/{len(urls)}] Failed: {error_msg}"))
                
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
            
            self.message_queue.put(("complete", {
                "successful": successful,
                "failed": failed,
                "total": len(urls)
            }))
            
        except Exception as e:
            print(f"[DOWNLOAD DEBUG CRITICAL ERROR] {e}")
            import traceback
            traceback.print_exc()
            self.message_queue.put(("error", f"Download error: {e}"))
    
    def stop_download(self):
        """Stop the download process"""
        self.overall_progress_bar.stop()
        self.current_progress_bar.stop()
        self.overall_progress_var.set("Download stopped")
        self.current_progress_var.set("Stopped")
        self.download_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("Download stopped by user", "orange")
    
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
                        messagebox.showwarning(
                            "Download Complete",
                            f"Download completed with some failures:\n"
                            f"Successful: {data['successful']}\n"
                            f"Failed: {data['failed']}\n"
                            f"Check the log and individual video status for details."
                        )
                    else:
                        messagebox.showinfo(
                            "Download Complete",
                            f"All {data['successful']} downloads completed successfully!"
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
