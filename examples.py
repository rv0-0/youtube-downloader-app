"""
Example usage of the YouTube Downloader
"""

from youtube_downloader import YouTubeDownloader
from colorama import Fore, init
init(autoreset=True)


def example_single_video():
    """Example: Download a single video"""
    print(f"{Fore.CYAN}Example 1: Single Video Download")
    print("-" * 40)
    
    downloader = YouTubeDownloader()
    
    # Example single video URL (replace with actual URL)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"Downloading single video: {video_url}")
    success = downloader.download_url(video_url)
    
    if success:
        print(f"{Fore.GREEN}Single video downloaded successfully!")
    else:
        print(f"{Fore.RED}Failed to download single video")


def example_playlist():
    """Example: Download a playlist"""
    print(f"\n{Fore.CYAN}Example 2: Playlist Download")
    print("-" * 40)
    
    downloader = YouTubeDownloader()
    
    # Example playlist URL (replace with actual URL)
    playlist_url = "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M"
    
    print(f"Downloading playlist: {playlist_url}")
    success = downloader.download_url(playlist_url)
    
    if success:
        print(f"{Fore.GREEN}Playlist downloaded successfully!")
    else:
        print(f"{Fore.RED}Failed to download playlist")


def example_multiple_urls():
    """Example: Download multiple URLs (mix of videos and playlists)"""
    print(f"\n{Fore.CYAN}Example 3: Multiple URLs Download")
    print("-" * 40)
    
    downloader = YouTubeDownloader()
    
    # Mix of single videos and playlists
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Single video
        "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",  # Playlist
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
    ]
    
    print(f"Downloading {len(urls)} URLs...")
    results = downloader.download_multiple_urls(urls)
    
    # Print detailed results
    print(f"\n{Fore.CYAN}Detailed Results:")
    for url, success in results.items():
        status = f"{Fore.GREEN}✓ Success" if success else f"{Fore.RED}✗ Failed"
        print(f"  {url} - {status}")


def example_custom_path():
    """Example: Download to custom directory with subtitle options"""
    print(f"\n{Fore.CYAN}Example 4: Custom Download Path with Subtitles")
    print("-" * 40)
    
    # Create downloader with custom path and subtitle settings
    custom_downloader = YouTubeDownloader(
        download_path="MyVideos",
        download_subtitles=True,  # Download English subtitles
        embed_subtitles=False     # Keep as separate .srt files
    )
    
    # This will create folders: MyVideos/Single Videos/ and MyVideos/Playlists/
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"Downloading to custom path: MyVideos/")
    print(f"Subtitle settings: Download=True, Embed=False")
    success = custom_downloader.download_url(video_url)
    
    if success:
        print(f"{Fore.GREEN}Video downloaded to custom directory with subtitles!")
    else:
        print(f"{Fore.RED}Failed to download to custom directory")


def example_subtitle_options():
    """Example: Different subtitle configurations"""
    print(f"\n{Fore.CYAN}Example 5: Subtitle Configuration Options")
    print("-" * 40)
    
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Option 1: Download subtitles as separate files (default)
    print(f"{Fore.YELLOW}Option 1: Separate subtitle files (.srt)")
    downloader1 = YouTubeDownloader(
        download_path="Downloads_SeparateSubs",
        download_subtitles=True,
        embed_subtitles=False
    )
    
    # Option 2: Embed subtitles in video file
    print(f"{Fore.YELLOW}Option 2: Embedded subtitles")
    downloader2 = YouTubeDownloader(
        download_path="Downloads_EmbeddedSubs",
        download_subtitles=True,
        embed_subtitles=True
    )
    
    # Option 3: No subtitles
    print(f"{Fore.YELLOW}Option 3: No subtitles")
    downloader3 = YouTubeDownloader(
        download_path="Downloads_NoSubs",
        download_subtitles=False
    )
    
    # Option 4: Custom subtitle languages
    print(f"{Fore.YELLOW}Option 4: Multiple languages")
    downloader4 = YouTubeDownloader(
        download_path="Downloads_MultiLang",
        download_subtitles=True,
        subtitle_languages=['en', 'es', 'fr', 'de']  # English, Spanish, French, German
    )
    
    print(f"{Fore.GREEN}All subtitle configuration examples created!")
    print(f"You can use any of these configurations for your downloads.")


def interactive_example():
    """Interactive example where user can input their own URLs"""
    print(f"\n{Fore.CYAN}Example 6: Interactive Download")
    print("-" * 40)
    
    downloader = YouTubeDownloader()
    
    print(f"{Fore.YELLOW}Enter your YouTube URLs (press Enter when done):")
    
    urls = []
    while True:
        url = input(f"{Fore.CYAN}URL: ").strip()
        if not url:
            break
        
        if 'youtube.com' in url or 'youtu.be' in url:
            urls.append(url)
            print(f"{Fore.GREEN}✓ Added: {url}")
        else:
            print(f"{Fore.RED}✗ Invalid YouTube URL")
    
    if urls:
        print(f"\n{Fore.CYAN}Starting downloads...")
        results = downloader.download_multiple_urls(urls)
        
        successful = sum(1 for success in results.values() if success)
        print(f"\n{Fore.GREEN}Successfully downloaded {successful}/{len(urls)} items")
    else:
        print(f"{Fore.YELLOW}No URLs provided")


if __name__ == "__main__":
    print(f"{Fore.MAGENTA}🎬 YouTube Downloader - Examples")
    print("=" * 50)
    
    # Note: These examples use placeholder URLs
    # Replace with actual YouTube URLs to test
    
    print(f"{Fore.YELLOW}Note: Replace example URLs with actual YouTube URLs to test")
    print(f"{Fore.YELLOW}Current examples use placeholder URLs that may not work\n")
    
    try:
        # Run examples (commented out to avoid errors with placeholder URLs)
        # example_single_video()
        # example_playlist()
        # example_multiple_urls()
        # example_custom_path()
        # example_subtitle_options()
        
        # Run interactive example
        interactive_example()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Examples interrupted by user")
    except Exception as e:
        print(f"{Fore.RED}Error in examples: {e}")
        print(f"{Fore.YELLOW}Make sure to install dependencies: pip install -r requirements.txt")
