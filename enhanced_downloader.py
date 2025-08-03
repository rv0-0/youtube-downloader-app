"""
Enhanced YouTube Downloader with multiple fallback strategies
This version includes additional methods to handle problematic videos
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

try:
    import yt_dlp
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


class EnhancedYouTubeDownloader:
    """
    Enhanced YouTube downloader with multiple fallback strategies
    """
    
    def __init__(self, download_path: str = "Downloads"):
        self.download_path = Path(download_path)
        self.single_videos_path = self.download_path / "Single Videos"
        self.playlists_path = self.download_path / "Playlists"
        
        # Create download directories
        self.download_path.mkdir(exist_ok=True)
        self.single_videos_path.mkdir(exist_ok=True)
        self.playlists_path.mkdir(exist_ok=True)
        
        # Primary options (best quality)
        self.primary_opts = {
            'format': 'best[height<=1080]/best',
            'restrictfilenames': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
        }
        
        # Fallback options (more compatible)
        self.fallback_opts = {
            'format': 'worst[height>=480]/worst',  # Lower quality for compatibility
            'restrictfilenames': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': True,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 5,
            'sleep_interval': 2,
            'max_sleep_interval': 10,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        # Audio-only fallback for very problematic videos
        self.audio_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': True,
            'retries': 5,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem usage."""
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        filename = filename.strip(' .')
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def is_playlist_url(self, url: str) -> bool:
        """Determine if a URL is a playlist or single video."""
        try:
            parsed_url = urlparse(url)
            if 'playlist' in parsed_url.path.lower():
                return True
            query_params = parse_qs(parsed_url.query)
            if 'list' in query_params:
                list_id = query_params['list'][0]
                if list_id.startswith(('PL', 'UU', 'FL', 'RD', 'LL')):
                    return True
            return False
        except Exception:
            return False
    
    def download_with_strategy(self, url: str, output_path: str, strategy: str = "primary") -> bool:
        """
        Download using a specific strategy
        
        Args:
            url (str): Video URL
            output_path (str): Output path template
            strategy (str): Download strategy ('primary', 'fallback', 'audio')
            
        Returns:
            bool: Success status
        """
        try:
            if strategy == "primary":
                opts = self.primary_opts.copy()
            elif strategy == "fallback":
                opts = self.fallback_opts.copy()
            elif strategy == "audio":
                opts = self.audio_opts.copy()
            else:
                opts = self.primary_opts.copy()
            
            opts['outtmpl'] = output_path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Strategy '{strategy}' failed: {e}")
            return False
    
    def download_single_video_enhanced(self, url: str) -> bool:
        """
        Download a single video with multiple fallback strategies
        """
        print(f"{Fore.BLUE}Downloading single video with enhanced strategies...")
        
        output_template = str(self.single_videos_path / '%(title)s.%(ext)s')
        
        # Strategy 1: Try primary method (best quality)
        print(f"{Fore.CYAN}Trying primary strategy (best quality)...")
        if self.download_with_strategy(url, output_template, "primary"):
            print(f"{Fore.GREEN}✓ Successfully downloaded with primary strategy")
            return True
        
        # Strategy 2: Try fallback method (lower quality, more compatible)
        print(f"{Fore.YELLOW}Primary failed, trying fallback strategy (lower quality)...")
        if self.download_with_strategy(url, output_template, "fallback"):
            print(f"{Fore.GREEN}✓ Successfully downloaded with fallback strategy")
            return True
        
        # Strategy 3: Try audio-only as last resort
        print(f"{Fore.YELLOW}Video download failed, trying audio-only...")
        audio_template = str(self.single_videos_path / '%(title)s.%(ext)s')
        if self.download_with_strategy(url, audio_template, "audio"):
            print(f"{Fore.GREEN}✓ Successfully downloaded audio-only version")
            return True
        
        print(f"{Fore.RED}✗ All download strategies failed")
        return False
    
    def download_playlist_enhanced(self, url: str) -> bool:
        """
        Download a playlist with enhanced error handling
        """
        try:
            print(f"{Fore.BLUE}Analyzing playlist...")
            
            # Get playlist info
            opts = {'quiet': True, 'extract_flat': True, 'force_json': True}
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    print(f"{Fore.RED}Error getting playlist info: {e}")
                    return False
            
            if not info:
                print(f"{Fore.RED}Failed to get playlist information")
                return False
            
            playlist_title = info.get('title', 'Unknown Playlist')
            playlist_title = self.sanitize_filename(playlist_title)
            entries = info.get('entries', [])
            
            if not entries:
                print(f"{Fore.RED}No videos found in playlist")
                return False
            
            print(f"{Fore.GREEN}Playlist: {playlist_title}")
            print(f"{Fore.GREEN}Videos found: {len(entries)}")
            
            # Create playlist folder
            playlist_folder = self.playlists_path / playlist_title
            playlist_folder.mkdir(exist_ok=True)
            
            # Download videos individually for better error handling
            successful_downloads = 0
            failed_downloads = 0
            
            for i, entry in enumerate(entries, 1):
                if entry is None:
                    continue
                
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                video_title = entry.get('title', f'Video {i}')
                
                print(f"\n{Fore.CYAN}[{i}/{len(entries)}] Downloading: {video_title[:50]}...")
                
                # Create numbered filename
                safe_title = self.sanitize_filename(video_title)
                output_template = str(playlist_folder / f'{i:02d} - {safe_title}.%(ext)s')
                
                # Try multiple strategies for each video
                success = False
                
                # Primary strategy
                if self.download_with_strategy(video_url, output_template, "primary"):
                    successful_downloads += 1
                    success = True
                    print(f"{Fore.GREEN}✓ Downloaded successfully")
                
                # Fallback strategy
                elif self.download_with_strategy(video_url, output_template, "fallback"):
                    successful_downloads += 1
                    success = True
                    print(f"{Fore.GREEN}✓ Downloaded with fallback strategy")
                
                # Audio-only strategy
                elif self.download_with_strategy(video_url, output_template, "audio"):
                    successful_downloads += 1
                    success = True
                    print(f"{Fore.GREEN}✓ Downloaded audio-only")
                
                if not success:
                    failed_downloads += 1
                    print(f"{Fore.RED}✗ Failed to download")
                
                # Small delay between downloads
                time.sleep(1)
            
            # Report results
            print(f"\n{Fore.CYAN}Playlist download summary:")
            print(f"{Fore.GREEN}✓ Successful: {successful_downloads}/{len(entries)}")
            print(f"{Fore.RED}✗ Failed: {failed_downloads}/{len(entries)}")
            
            if successful_downloads > 0:
                print(f"{Fore.GREEN}✓ Playlist '{playlist_title}' downloaded with {successful_downloads} videos")
                return True
            else:
                print(f"{Fore.RED}✗ No videos were successfully downloaded")
                return False
            
        except Exception as e:
            print(f"{Fore.RED}Error downloading playlist: {e}")
            return False
    
    def download_url(self, url: str) -> bool:
        """Download from a URL using enhanced methods"""
        print(f"{Fore.CYAN}Processing URL: {url}")
        
        if self.is_playlist_url(url):
            print(f"{Fore.YELLOW}Detected: Playlist")
            return self.download_playlist_enhanced(url)
        else:
            print(f"{Fore.YELLOW}Detected: Single Video")
            return self.download_single_video_enhanced(url)
    
    def download_multiple_urls(self, urls: List[str]) -> Dict[str, bool]:
        """Download from multiple URLs"""
        results = {}
        total_urls = len(urls)
        
        print(f"{Fore.MAGENTA}Starting enhanced download of {total_urls} URL(s)...")
        print("=" * 60)
        
        for i, url in enumerate(urls, 1):
            print(f"\n{Fore.MAGENTA}[{i}/{total_urls}] Processing URL...")
            
            try:
                success = self.download_url(url.strip())
                results[url] = success
                
                if success:
                    print(f"{Fore.GREEN}✓ Completed successfully")
                else:
                    print(f"{Fore.RED}✗ Failed to download")
                    
            except Exception as e:
                print(f"{Fore.RED}✗ Error: {e}")
                results[url] = False
            
            # Add delay between downloads
            if i < total_urls:
                time.sleep(2)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"{Fore.MAGENTA}Enhanced Download Summary:")
        successful = sum(1 for success in results.values() if success)
        failed = total_urls - successful
        
        print(f"{Fore.GREEN}Successful: {successful}")
        print(f"{Fore.RED}Failed: {failed}")
        
        return results


def main():
    """Main function for enhanced downloader"""
    print(f"{Fore.CYAN}🎬 Enhanced YouTube Downloader")
    print("=" * 50)
    print(f"{Fore.YELLOW}This version includes multiple fallback strategies")
    print(f"{Fore.YELLOW}for handling problematic videos and playlists.")
    print()
    
    downloader = EnhancedYouTubeDownloader()
    
    print(f"{Fore.YELLOW}Enter YouTube URLs (one per line).")
    print(f"{Fore.YELLOW}Press Enter twice when done, or type 'quit' to exit.\n")
    
    urls = []
    while True:
        try:
            url = input(f"{Fore.CYAN}URL {len(urls) + 1}: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                break
            
            if not url:
                if urls:
                    break
                else:
                    continue
            
            if 'youtube.com' in url or 'youtu.be' in url:
                urls.append(url)
                print(f"{Fore.GREEN}✓ Added: {url}")
            else:
                print(f"{Fore.RED}✗ Invalid YouTube URL")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled by user")
            return
        except EOFError:
            break
    
    if not urls:
        print(f"{Fore.RED}No valid URLs provided")
        return
    
    print(f"\n{Fore.CYAN}Starting enhanced downloads...")
    results = downloader.download_multiple_urls(urls)
    
    print(f"\n{Fore.CYAN}Enhanced downloads completed!")
    print(f"{Fore.CYAN}Check the 'Downloads' folder for your videos.")


if __name__ == "__main__":
    main()
