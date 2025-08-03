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


class YouTubeDownloader:
    """
    A comprehensive YouTube downloader that handles both single videos and playlists.
    Automatically detects URL types and organizes downloads appropriately.
    """
    
    def __init__(self, download_path: str = "Downloads", download_subtitles: bool = True, 
                 embed_subtitles: bool = False, subtitle_languages: List[str] = None):
        self.download_path = Path(download_path)
        self.single_videos_path = self.download_path / "Single Videos"
        self.playlists_path = self.download_path / "Playlists"
        
        # Subtitle configuration
        self.download_subtitles = download_subtitles
        self.embed_subtitles = embed_subtitles
        self.subtitle_languages = subtitle_languages or ['en', 'en-US', 'en-GB', 'en.*']
        
        # Create download directories
        self.download_path.mkdir(exist_ok=True)
        self.single_videos_path.mkdir(exist_ok=True)
        self.playlists_path.mkdir(exist_ok=True)
        
        # Configure yt-dlp options for single videos
        self.single_video_opts = {
            'format': 'best[height<=1080]/best',  # Best quality up to 1080p, fallback to best available
            'outtmpl': str(self.single_videos_path / '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'writesubtitles': self.download_subtitles,
            'writeautomaticsub': self.download_subtitles,
            'subtitleslangs': self.subtitle_languages,
            'subtitlesformat': 'srt/vtt/best',
            'embedsubs': self.embed_subtitles,
            'ignoreerrors': True,  # Continue on errors
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'best',
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
        }
        
        # Configure yt-dlp options for playlists
        self.playlist_opts = {
            'format': 'best[height<=1080]/best',  # Best quality up to 1080p, fallback to best available
            'restrictfilenames': True,
            'writesubtitles': self.download_subtitles,
            'writeautomaticsub': self.download_subtitles,
            'subtitleslangs': self.subtitle_languages,
            'subtitlesformat': 'srt/vtt/best',
            'embedsubs': self.embed_subtitles,
            'ignoreerrors': True,  # Continue on errors for playlists
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'best',
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
        }
    
    def configure_subtitles(self, download_subtitles: bool = True, embed_subtitles: bool = False, 
                           subtitle_languages: List[str] = None):
        """
        Configure subtitle download settings.
        
        Args:
            download_subtitles (bool): Whether to download subtitles
            embed_subtitles (bool): Whether to embed subtitles in video file
            subtitle_languages (List[str]): List of subtitle languages to download
        """
        self.download_subtitles = download_subtitles
        self.embed_subtitles = embed_subtitles
        if subtitle_languages:
            self.subtitle_languages = subtitle_languages
        
        # Update options
        self._update_subtitle_options()
        
        print(f"📝 Subtitle settings updated:")
        print(f"   Download subtitles: {self.download_subtitles}")
        print(f"   Embed subtitles: {self.embed_subtitles}")
        print(f"   Languages: {', '.join(self.subtitle_languages)}")
    
    def _update_subtitle_options(self):
        """Update subtitle options in both single video and playlist configurations."""
        subtitle_opts = {
            'writesubtitles': self.download_subtitles,
            'writeautomaticsub': self.download_subtitles,
            'subtitleslangs': self.subtitle_languages,
            'embedsubs': self.embed_subtitles,
        }
        
        self.single_video_opts.update(subtitle_opts)
        self.playlist_opts.update(subtitle_opts)
    
    def is_playlist_url(self, url: str) -> bool:
        """
        Determine if a URL is a playlist or single video.
        
        Args:
            url (str): YouTube URL to check
            
        Returns:
            bool: True if URL is a playlist, False otherwise
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Check for playlist indicators
            if 'playlist' in parsed_url.path.lower():
                return True
            
            # Check query parameters for playlist list
            query_params = parse_qs(parsed_url.query)
            if 'list' in query_params:
                # Some single videos can have list parameter, so we need to check further
                list_id = query_params['list'][0]
                # Playlist IDs typically start with 'PL', 'UU', 'FL', etc.
                if list_id.startswith(('PL', 'UU', 'FL', 'RD', 'LL')):
                    return True
            
            return False
        except Exception:
            return False
    
    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """
        Extract playlist information without downloading.
        
        Args:
            url (str): Playlist URL
            
        Returns:
            Optional[Dict]: Playlist information or None if failed
        """
        try:
            opts = {
                'quiet': True,
                'extract_flat': True,
                'force_json': True
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"{Fore.RED}Error extracting playlist info: {e}")
            return None
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe filesystem usage.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove or replace illegal characters
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def download_single_video(self, url: str) -> bool:
        """
        Download a single video.
        
        Args:
            url (str): Video URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"{Fore.BLUE}Downloading single video...")
            
            with yt_dlp.YoutubeDL(self.single_video_opts) as ydl:
                # Extract video info first
                try:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown Title')
                    print(f"{Fore.GREEN}Title: {title}")
                    
                    # Check if video is available
                    if info.get('availability') == 'private':
                        print(f"{Fore.RED}Video is private and cannot be downloaded")
                        return False
                    elif info.get('availability') == 'premium_only':
                        print(f"{Fore.RED}Video requires premium membership")
                        return False
                    
                except Exception as e:
                    print(f"{Fore.RED}Error getting video info: {e}")
                    print(f"{Fore.YELLOW}Attempting direct download...")
                
                # Download the video
                ydl.download([url])
                print(f"{Fore.GREEN}✓ Successfully downloaded single video")
                return True
                
        except yt_dlp.utils.DownloadError as e:
            if "403" in str(e) or "Forbidden" in str(e):
                print(f"{Fore.RED}Access denied (403 Forbidden). This video may be:")
                print(f"{Fore.RED}  - Age restricted")
                print(f"{Fore.RED}  - Region blocked")
                print(f"{Fore.RED}  - Requires login")
                print(f"{Fore.YELLOW}Try using a different URL or check if the video is publicly accessible")
            elif "404" in str(e):
                print(f"{Fore.RED}Video not found (404). The video may have been deleted or made private")
            else:
                print(f"{Fore.RED}Download error: {e}")
            return False
        except Exception as e:
            print(f"{Fore.RED}Error downloading video: {e}")
            return False
    
    def download_playlist(self, url: str) -> bool:
        """
        Download an entire playlist with proper organization.
        
        Args:
            url (str): Playlist URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"{Fore.BLUE}Analyzing playlist...")
            
            # Get playlist info
            playlist_info = self.get_playlist_info(url)
            if not playlist_info:
                print(f"{Fore.RED}Failed to get playlist information")
                return False
            
            playlist_title = playlist_info.get('title', 'Unknown Playlist')
            playlist_title = self.sanitize_filename(playlist_title)
            entries = playlist_info.get('entries', [])
            
            if not entries:
                print(f"{Fore.RED}No videos found in playlist")
                return False
            
            print(f"{Fore.GREEN}Playlist: {playlist_title}")
            print(f"{Fore.GREEN}Videos found: {len(entries)}")
            
            # Create playlist folder
            playlist_folder = self.playlists_path / playlist_title
            playlist_folder.mkdir(exist_ok=True)
            
            # Configure output template for numbered files
            playlist_opts = self.playlist_opts.copy()
            playlist_opts['outtmpl'] = str(playlist_folder / '%(playlist_index)02d - %(title)s.%(ext)s')
            
            # Download the playlist with better error handling
            successful_downloads = 0
            failed_downloads = 0
            
            try:
                with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                    ydl.download([url])
                    
                # Count successful downloads by checking the folder
                downloaded_files = list(playlist_folder.glob('*.mp4')) + list(playlist_folder.glob('*.webm')) + list(playlist_folder.glob('*.mkv'))
                successful_downloads = len(downloaded_files)
                failed_downloads = len(entries) - successful_downloads
                
            except yt_dlp.utils.DownloadError as e:
                if "403" in str(e) or "Forbidden" in str(e):
                    print(f"{Fore.RED}Access denied for some videos. These may be:")
                    print(f"{Fore.RED}  - Age restricted")
                    print(f"{Fore.RED}  - Region blocked")
                    print(f"{Fore.RED}  - Require login")
                elif "404" in str(e):
                    print(f"{Fore.RED}Some videos in the playlist were not found (deleted or private)")
                else:
                    print(f"{Fore.RED}Download error: {e}")
                
                # Still count what was downloaded
                downloaded_files = list(playlist_folder.glob('*.mp4')) + list(playlist_folder.glob('*.webm')) + list(playlist_folder.glob('*.mkv'))
                successful_downloads = len(downloaded_files)
                failed_downloads = len(entries) - successful_downloads
            
            # Report results
            if successful_downloads > 0:
                print(f"{Fore.GREEN}✓ Downloaded {successful_downloads}/{len(entries)} videos from playlist: {playlist_title}")
                if failed_downloads > 0:
                    print(f"{Fore.YELLOW}⚠ {failed_downloads} videos failed to download (may be restricted/unavailable)")
                return True
            else:
                print(f"{Fore.RED}✗ No videos were successfully downloaded from playlist")
                return False
            
        except Exception as e:
            print(f"{Fore.RED}Error downloading playlist: {e}")
            return False
    
    def download_url(self, url: str) -> bool:
        """
        Download from a URL (automatically detects playlist vs single video).
        
        Args:
            url (str): YouTube URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Processing URL: {url}")
        
        if self.is_playlist_url(url):
            print(f"{Fore.YELLOW}Detected: Playlist")
            return self.download_playlist(url)
        else:
            print(f"{Fore.YELLOW}Detected: Single Video")
            return self.download_single_video(url)
    
    def download_multiple_urls(self, urls: List[str]) -> Dict[str, bool]:
        """
        Download from multiple URLs.
        
        Args:
            urls (List[str]): List of YouTube URLs
            
        Returns:
            Dict[str, bool]: Results for each URL
        """
        results = {}
        total_urls = len(urls)
        
        print(f"{Fore.MAGENTA}Starting download of {total_urls} URL(s)...")
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
            
            # Add small delay between downloads
            if i < total_urls:
                time.sleep(1)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"{Fore.MAGENTA}Download Summary:")
        successful = sum(1 for success in results.values() if success)
        failed = total_urls - successful
        
        print(f"{Fore.GREEN}Successful: {successful}")
        print(f"{Fore.RED}Failed: {failed}")
        
        if failed > 0:
            print(f"\n{Fore.RED}Failed URLs:")
            for url, success in results.items():
                if not success:
                    print(f"  - {url}")
        
        return results


def main():
    """Main function for command-line interface."""
    print(f"{Fore.CYAN}🎬 YouTube Downloader")
    print("=" * 50)
    
    # Ask about subtitle preferences
    print(f"\n{Fore.YELLOW}Subtitle Options:")
    while True:
        try:
            download_subs = input(f"{Fore.CYAN}Download English subtitles? (y/n, default: y): ").strip().lower()
            if download_subs in ['', 'y', 'yes']:
                download_subtitles = True
                break
            elif download_subs in ['n', 'no']:
                download_subtitles = False
                break
            else:
                print(f"{Fore.RED}Please enter 'y' for yes or 'n' for no")
        except (KeyboardInterrupt, EOFError):
            download_subtitles = True
            break
    
    embed_subs = False
    if download_subtitles:
        while True:
            try:
                embed_input = input(f"{Fore.CYAN}Embed subtitles in video file? (y/n, default: n): ").strip().lower()
                if embed_input in ['', 'n', 'no']:
                    embed_subs = False
                    break
                elif embed_input in ['y', 'yes']:
                    embed_subs = True
                    break
                else:
                    print(f"{Fore.RED}Please enter 'y' for yes or 'n' for no")
            except (KeyboardInterrupt, EOFError):
                embed_subs = False
                break
    
    downloader = YouTubeDownloader(
        download_subtitles=download_subtitles,
        embed_subtitles=embed_subs
    )
    
    print(f"\n{Fore.GREEN}📝 Subtitle settings:")
    print(f"   Download: {'Yes' if download_subtitles else 'No'}")
    if download_subtitles:
        print(f"   Embed: {'Yes' if embed_subs else 'No (separate .srt files)'}")
        print(f"   Languages: English (en, en-US, en-GB)")
    
    print(f"\n{Fore.YELLOW}Enter YouTube URLs (one per line).")
    print(f"{Fore.YELLOW}Supports both single videos and playlists.")
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
            
            # Basic URL validation
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
    
    print(f"\n{Fore.CYAN}Starting downloads...")
    results = downloader.download_multiple_urls(urls)
    
    print(f"\n{Fore.CYAN}Downloads completed!")
    print(f"{Fore.CYAN}Check the 'Downloads' folder for your videos.")


if __name__ == "__main__":
    main()
