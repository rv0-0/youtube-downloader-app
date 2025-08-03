"""
Download manager for the YouTube Downloader GUI
Handles download processes, threading, and process management
"""

import threading
import queue
import subprocess
import signal
import os
import time
import traceback
import sys

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

from youtube_downloader import YouTubeDownloader
from .constants import PROCESS_TERMINATION_TIMEOUT


class DownloadManager:
    """Manages download processes and threading"""
    
    def __init__(self, message_queue):
        self.message_queue = message_queue
        self.downloader = None
        self.download_stopped = False
        self.running_processes = []
        self.download_thread = None
        self.current_downloading_url = None
    
    def start_download(self, urls, settings, progress_tracker):
        """Start the download process in a separate thread"""
        # Reset state
        self.download_stopped = False
        self.running_processes.clear()
        
        # Start download thread
        self.download_thread = threading.Thread(
            target=self._download_worker, 
            args=(urls, settings, progress_tracker), 
            daemon=True
        )
        self.download_thread.start()
    
    def stop_download(self):
        """Stop the download process"""
        print("[DOWNLOAD MGR DEBUG] Stop download requested")
        self.download_stopped = True
        
        # Terminate all running processes
        self._terminate_all_processes()
        
        # Wait for thread to finish gracefully (with timeout)
        if self.download_thread and self.download_thread.is_alive():
            print("[DOWNLOAD MGR DEBUG] Waiting for download thread to finish...")
            self.download_thread.join(timeout=PROCESS_TERMINATION_TIMEOUT)
            
            if self.download_thread.is_alive():
                print("[DOWNLOAD MGR DEBUG] Download thread did not finish in time")
        
        print("[DOWNLOAD MGR DEBUG] Download stop completed")
    
    def _download_worker(self, urls, settings, progress_tracker):
        """Worker function for downloading (runs in separate thread)"""
        try:
            # Get selected format FIRST
            selected_format = settings['format']
            
            # Create downloader instance with settings
            self.downloader = YouTubeDownloader(
                download_path=settings['path'],
                download_subtitles=settings['download_subtitles'],
                embed_subtitles=settings['embed_subtitles']
            )
            
            # Set the format from GUI selection
            self.downloader.set_format(selected_format)
            
            # Create a custom progress hook
            def progress_hook(d):
                try:
                    # Check if download was stopped
                    if self.download_stopped:
                        print(f"[DOWNLOAD DEBUG] Download stopped flag detected in progress hook")
                        self._terminate_all_processes()
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
                        if any(skip_term in filename.lower() for skip_term in ['fragment', '.vtt', '.srt', 'temp']):
                            return
                        
                        if total and downloaded:
                            progress_percent = (downloaded / total) * 100
                            speed = d.get('speed', 0)
                            eta = d.get('eta', 0)
                            
                            # Format speed and ETA safely
                            speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "N/A"
                            eta_str = f"{eta}s" if eta else "N/A"
                            
                            # Update current progress
                            progress_text = f"Downloading: {progress_percent:.1f}% - {speed_str} - ETA: {eta_str}"
                            self.message_queue.put(("current_progress", progress_text, progress_percent))
                            
                            # Update video progress
                            if self.current_downloading_url:
                                self.message_queue.put(("video_progress", {
                                    "url": self.current_downloading_url,
                                    "status": "Downloading",
                                    "progress": progress_percent
                                }))
                                
                    elif d['status'] == 'finished':
                        print(f"[DOWNLOAD DEBUG] Download finished: {d.get('filename', 'N/A')}")
                        if self.current_downloading_url:
                            self.message_queue.put(("video_progress", {
                                "url": self.current_downloading_url,
                                "status": "Completed",
                                "progress": 100
                            }))
                            
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG] Error in progress hook: {e}")
                    traceback.print_exc()
            
            # Process each URL
            results = {}
            for i, url in enumerate(urls, 1):
                if self.download_stopped:
                    print(f"[DOWNLOAD DEBUG] Download stopped, breaking URL loop")
                    break
                
                print(f"[DOWNLOAD DEBUG] ===== Processing URL {i}/{len(urls)} =====")
                print(f"[DOWNLOAD DEBUG] URL: {url}")
                
                try:
                    self.current_downloading_url = url
                    
                    # Update current progress
                    self.message_queue.put(("current_progress", f"Processing URL {i}/{len(urls)}: {url[:50]}...", 0))
                    self.message_queue.put(("log", f"Starting download {i}/{len(urls)}: {url}"))
                    
                    # Use our custom download with progress tracking instead of the built-in method
                    result = self._download_with_progress(url, selected_format, progress_hook, progress_tracker)
                    
                    if result:
                        results[url] = True
                        self.message_queue.put(("log", f"✅ Successfully downloaded: {url}"))
                        # Mark as completed
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Completed",
                            "progress": 100
                        }))
                    else:
                        results[url] = False
                        self.message_queue.put(("log", f"❌ Failed to download: {url}"))
                        self.message_queue.put(("video_progress", {
                            "url": url,
                            "status": "Failed",
                            "progress": 0
                        }))
                    
                    # Update overall progress
                    self.message_queue.put(("overall_progress", f"Completed {i}/{len(urls)} downloads"))
                    
                except Exception as e:
                    print(f"[DOWNLOAD DEBUG] Error processing URL {url}: {e}")
                    traceback.print_exc()
                    results[url] = False
                    self.message_queue.put(("log", f"❌ Error downloading {url}: {str(e)}"))
                    self.message_queue.put(("video_progress", {
                        "url": url,
                        "status": "Failed",
                        "progress": 0
                    }))
            
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
            traceback.print_exc()
            self.message_queue.put(("error", f"Download error: {e}"))
    
    def _download_with_progress(self, url, selected_format, progress_hook, progress_tracker):
        """Download a single URL with progress tracking"""
        try:
            # Check if this is a playlist
            info = self.downloader.get_info(url)
            if not info:
                return False
            
            is_playlist = self.downloader.is_playlist_url(url)
            
            if is_playlist:
                print(f"[DOWNLOAD DEBUG] Detected playlist")
                
                # Get full playlist info
                playlist_info = self.downloader.get_playlist_info(url)
                if not playlist_info or 'entries' not in playlist_info:
                    self.message_queue.put(("log", f"❌ Could not get playlist information"))
                    return False
                
                # Filter out None entries (unavailable videos)
                available_entries = [entry for entry in playlist_info['entries'] if entry is not None]
                unavailable_count = len(playlist_info['entries']) - len(available_entries)
                
                if unavailable_count > 0:
                    self.message_queue.put(("log", f"⚠️ {unavailable_count} videos in playlist are unavailable (private/deleted)"))
                
                # Clear existing progress and add playlist videos
                progress_tracker.clear_video_progress()
                for idx, entry in enumerate(available_entries, 1):
                    if entry and 'title' in entry:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        progress_tracker.add_video_to_progress(idx, entry['title'], video_url)
                
                # Update total videos count
                progress_tracker.total_videos = len(available_entries)
                self.message_queue.put(("log", f"📋 Playlist: {len(available_entries)} videos ready for download"))
                
                # Create custom yt-dlp options with progress hook
                ydl_opts = self.downloader.playlist_opts.copy()
                ydl_opts['format'] = selected_format
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Download playlist with progress tracking
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                return True
                
            else:
                # Single video
                video_title = info.get('title', 'Unknown')
                
                # Create custom yt-dlp options with progress hook
                ydl_opts = self.downloader.single_video_opts.copy()
                ydl_opts['format'] = selected_format
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Download single video with progress tracking
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                return True
                
        except Exception as e:
            print(f"[DOWNLOAD MGR DEBUG] Error in _download_with_progress: {e}")
            traceback.print_exc()
            return False

    def _run_ytdlp_with_tracking(self, url, selected_format, progress_hook, progress_tracker):
        """Run yt-dlp download with process tracking for proper termination"""
        try:
            # Check if this is a playlist
            info = self.downloader.get_info(url)
            if not info:
                return False
            
            is_playlist = self.downloader.is_playlist_url(url)
            
            if is_playlist:
                print(f"[DOWNLOAD DEBUG] Detected playlist")
                
                # Get full playlist info
                playlist_info = self.downloader.get_playlist_info(url)
                if not playlist_info or 'entries' not in playlist_info:
                    self.message_queue.put(("log", f"❌ Could not get playlist information"))
                    return False
                
                # Filter out None entries (unavailable videos)
                available_entries = [entry for entry in playlist_info['entries'] if entry is not None]
                unavailable_count = len(playlist_info['entries']) - len(available_entries)
                
                if unavailable_count > 0:
                    self.message_queue.put(("log", f"⚠️ {unavailable_count} videos in playlist are unavailable (private/deleted)"))
                
                # Add available videos to progress tracker
                for idx, entry in enumerate(available_entries, 1):
                    if entry and 'title' in entry:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        progress_tracker.add_video_to_progress(idx, entry['title'], video_url)
                
                # Update total videos count
                progress_tracker.total_videos = len(available_entries)
                self.message_queue.put(("log", f"📋 Playlist: {len(available_entries)} videos ready for download"))
                
                # Use the downloader's built-in playlist download method
                success = self.downloader.download_playlist(url)
                
                if success:
                    # Mark all videos as completed
                    for idx, entry in enumerate(available_entries, 1):
                        if entry and 'title' in entry:
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            self.message_queue.put(("video_progress", {
                                "url": video_url,
                                "status": "Completed",
                                "progress": 100
                            }))
                
                return success
                
            else:
                # Single video
                progress_tracker.add_video_to_progress(1, info.get('title', 'Unknown'), url)
                progress_tracker.total_videos = 1
                
                # Use the downloader's built-in single video download method
                success = self.downloader.download_single_video(url)
                
                if success:
                    self.message_queue.put(("video_progress", {
                        "url": url,
                        "status": "Completed",
                        "progress": 100
                    }))
                
                return success
                
        except Exception as e:
            print(f"[DOWNLOAD MGR DEBUG] Error in _run_ytdlp_with_tracking: {e}")
            traceback.print_exc()
            return False
    
    def _terminate_all_processes(self):
        """Terminate all running yt-dlp processes"""
        try:
            print(f"[DOWNLOAD MGR DEBUG] Terminating {len(self.running_processes)} processes...")
            
            # First, try to terminate processes gracefully
            for proc in self.running_processes[:]:
                try:
                    if proc.poll() is None:  # Process is still running
                        print(f"[DOWNLOAD MGR DEBUG] Terminating process {proc.pid}")
                        proc.terminate()
                except Exception as e:
                    print(f"[DOWNLOAD MGR DEBUG] Error terminating process {proc.pid}: {e}")
            
            # Wait a moment for graceful termination
            time.sleep(1)
            
            # Force kill any remaining processes
            for proc in self.running_processes[:]:
                try:
                    if proc.poll() is None:  # Process is still running
                        print(f"[DOWNLOAD MGR DEBUG] Force killing process {proc.pid}")
                        proc.kill()
                        self.running_processes.remove(proc)
                except Exception as e:
                    print(f"[DOWNLOAD MGR DEBUG] Error killing process {proc.pid}: {e}")
            
            # Clear the process list
            self.running_processes.clear()
            
            # Additionally, try to kill any yt-dlp processes that might be running
            if PSUTIL_AVAILABLE:
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        if 'yt-dlp' in proc.info['name'] or 'python' in proc.info['name']:
                            if proc.info['cmdline'] and any('yt-dlp' in cmd for cmd in proc.info['cmdline']):
                                print(f"[DOWNLOAD MGR DEBUG] Killing yt-dlp process {proc.info['pid']}")
                                proc.kill()
                except Exception as e:
                    print(f"[DOWNLOAD MGR DEBUG] Error using psutil to kill processes: {e}")
            else:
                try:
                    if os.name == 'nt':  # Windows
                        os.system('taskkill /f /im python.exe 2>nul')
                        os.system('taskkill /f /im yt-dlp.exe 2>nul')
                    else:  # Unix-like
                        os.system('pkill -f yt-dlp 2>/dev/null')
                except Exception as e:
                    print(f"[DOWNLOAD MGR DEBUG] Error using system commands to kill processes: {e}")
                
        except Exception as e:
            print(f"[DOWNLOAD MGR DEBUG] Error in _terminate_all_processes: {e}")
            self.running_processes.clear()  # Clear the list anyway
