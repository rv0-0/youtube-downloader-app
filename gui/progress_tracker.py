"""
Progress tracking functionality for the YouTube Downloader GUI
Handles video progress tracking, overall progress calculation, and UI updates
"""

import tkinter as tk
from tkinter import ttk
from .constants import PROGRESS_COLUMNS, PROGRESS_COLUMN_WIDTHS


class ProgressTracker:
    """Manages progress tracking for individual videos and overall download progress"""
    
    def __init__(self, videos_tree, overall_progress_bar, current_progress_bar, 
                 overall_progress_var, current_progress_var):
        self.videos_tree = videos_tree
        self.overall_progress_bar = overall_progress_bar
        self.current_progress_bar = current_progress_bar
        self.overall_progress_var = overall_progress_var
        self.current_progress_var = current_progress_var
        
        # Progress tracking data
        self.video_progress = {}
        self.current_video_index = 0
        self.total_videos = 0
        
        # Setup tree columns if tree is available
        if self.videos_tree:
            self._setup_tree_columns()
    
    def _setup_tree_columns(self):
        """Configure the progress tree columns"""
        # Configure column headings and widths
        for col in PROGRESS_COLUMNS:
            self.videos_tree.heading(col, text=col if col != "Index" else "#")
            width = PROGRESS_COLUMN_WIDTHS[col]
            anchor = "center" if col in ["Index", "Status", "Progress"] else "w"
            self.videos_tree.column(col, width=width, anchor=anchor)
    
    def clear_video_progress(self):
        """Clear the video progress tree and reset tracking data"""
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        self.video_progress = {}
        self.current_video_index = 0
        self.total_videos = 0
    
    def add_video_to_progress(self, index, title, url):
        """Add a video to the progress tracking tree"""
        print(f"[PROGRESS DEBUG] add_video_to_progress called:")
        print(f"  Index: {index}")
        print(f"  Title: {title}")
        print(f"  URL: {url}")
        
        # Check if this URL is already being tracked (avoid duplicates)
        if url in self.video_progress:
            print(f"[PROGRESS DEBUG] URL already exists in progress tracking, skipping: {url}")
            return self.video_progress[url]["item_id"]
        
        # For playlist videos, don't use the total_videos in the display index
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
        
        print(f"[PROGRESS DEBUG] Video added to progress tracking:")
        print(f"  Item ID: {item_id}")
        print(f"  Total videos in tracking: {len(self.video_progress)}")
        
        return item_id
    
    def update_video_progress(self, url, status=None, progress=None, quality=None, title=None):
        """Update progress for a specific video"""
        print(f"[PROGRESS DEBUG] update_video_progress called:")
        print(f"  URL: {url}")
        print(f"  Status: {status}")
        print(f"  Progress: {progress}")
        print(f"  Quality: {quality}")
        print(f"  Title: {title}")
        
        # Find the video entry (with URL matching logic)
        video_info = self._find_video_by_url(url)
        if not video_info:
            print(f"[PROGRESS DEBUG] No matching URL found for: {url}")
            return
        
        item_id = video_info["item_id"]
        
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
            print(f"[PROGRESS DEBUG] Current tree values: {current_values}")
            
            # Update values for compact format (4 columns)
            if title:
                current_values[1] = title[:40] + "..." if len(title) > 40 else title
            if status:
                current_values[2] = status
            if progress is not None:
                if isinstance(progress, (int, float)):
                    current_values[3] = f"{progress:.1f}%"
                else:
                    current_values[3] = str(progress)
                
            print(f"[PROGRESS DEBUG] New tree values: {current_values}")
            self.videos_tree.item(item_id, values=current_values)
            
            # Scroll to current item if it's being downloaded
            if status in ["Downloading", "Processing"]:
                self.videos_tree.see(item_id)
                
            print(f"[PROGRESS DEBUG] Tree item updated successfully")
            
        except Exception as e:
            print(f"[PROGRESS DEBUG ERROR] Failed to update tree item: {e}")
    
    def _find_video_by_url(self, url):
        """Find video entry by URL with fuzzy matching for URL variations"""
        # Check for exact URL match first
        if url in self.video_progress:
            video_info = self.video_progress[url]
            print(f"[PROGRESS DEBUG] Found exact URL match")
            return video_info
        
        # Check for URL variants (with/without parameters, different formats)
        print(f"[PROGRESS DEBUG] No exact URL match found. Checking variants...")
        print(f"[PROGRESS DEBUG] Available URLs in tracking: {len(self.video_progress)} total")
        
        for key in self.video_progress.keys():
            if self._urls_match(url, key):
                print(f"[PROGRESS DEBUG] Found URL match by video ID")
                return self.video_progress[key]
        
        return None
    
    def _urls_match(self, url1, url2):
        """Check if two URLs refer to the same video by comparing video IDs"""
        try:
            # Extract video IDs from both URLs
            id1 = self._extract_video_id(url1)
            id2 = self._extract_video_id(url2)
            return id1 == id2 if id1 and id2 else False
        except Exception as e:
            print(f"[PROGRESS DEBUG] Error comparing URLs: {e}")
            return False
    
    def _extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        try:
            if 'youtube.com/watch?v=' in url:
                return url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                return url.split('youtu.be/')[1].split('?')[0]
            return None
        except Exception:
            return None
    
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
            
            print(f"[PROGRESS DEBUG] Overall progress updated: {completed}/{total} = {percentage:.1f}%")
    
    def update_current_progress(self, text, progress=None):
        """Update the current video progress display"""
        self.current_progress_var.set(text)
        if progress is not None:
            self.current_progress_bar["value"] = progress
    
    def reset_progress_bars(self):
        """Reset all progress bars to initial state"""
        self.overall_progress_bar["maximum"] = 100
        self.overall_progress_bar["value"] = 0
        self.current_progress_bar["maximum"] = 100
        self.current_progress_bar["value"] = 0
        self.overall_progress_var.set("Ready")
        self.current_progress_var.set("No active download")
