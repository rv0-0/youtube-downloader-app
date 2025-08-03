"""
Demo script showing YouTube Downloader features
Run this to see the downloader in action with example URLs
"""

from youtube_downloader import YouTubeDownloader
from colorama import Fore, init
import os

init(autoreset=True)


def demo_url_detection():
    """Demonstrate URL type detection"""
    print(f"{Fore.CYAN}🔍 URL Detection Demo")
    print("=" * 40)
    
    downloader = YouTubeDownloader()
    
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Single Video"),
        ("https://youtu.be/dQw4w9WgXcQ", "Single Video (Short URL)"),
        ("https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M", "Playlist"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest", "Video with Playlist"),
    ]
    
    for url, description in test_urls:
        is_playlist = downloader.is_playlist_url(url)
        detected_type = "Playlist" if is_playlist else "Single Video"
        status = "✅" if detected_type in description else "❌"
        
        print(f"{status} {description}")
        print(f"   URL: {url}")
        print(f"   Detected: {detected_type}")
        print()


def demo_folder_structure():
    """Show the folder structure that will be created"""
    print(f"{Fore.CYAN}📁 Folder Structure Demo")
    print("=" * 40)
    
    print("The downloader creates this structure:")
    print()
    print("Downloads/")
    print("├── Single Videos/")
    print("│   ├── Amazing Tutorial.mp4")
    print("│   ├── Amazing Tutorial.en.srt          # English subtitles")
    print("│   ├── Funny Cat Video.mp4")
    print("│   ├── Funny Cat Video.en.srt")
    print("│   └── Music Video.mp4")
    print("└── Playlists/")
    print("    ├── Python Programming Course/")
    print("    │   ├── 01 - Introduction to Python.mp4")
    print("    │   ├── 01 - Introduction to Python.en.srt")
    print("    │   ├── 02 - Variables and Data Types.mp4")
    print("    │   ├── 02 - Variables and Data Types.en.srt")
    print("    │   ├── 03 - Control Structures.mp4")
    print("    │   ├── 03 - Control Structures.en.srt")
    print("    │   ├── 04 - Functions and Modules.mp4")
    print("    │   └── 04 - Functions and Modules.en.srt")
    print("    └── Best Music 2024/")
    print("        ├── 01 - Song One.mp4")
    print("        ├── 01 - Song One.en.srt")
    print("        ├── 02 - Song Two.mp4")
    print("        ├── 02 - Song Two.en.srt")
    print("        ├── 03 - Song Three.mp4")
    print("        └── 03 - Song Three.en.srt")
    print()
    print(f"{Fore.YELLOW}Note: Subtitle files (.srt) are created when subtitle download is enabled")
    print()


def demo_filename_sanitization():
    """Demonstrate filename sanitization"""
    print(f"{Fore.CYAN}🧹 Filename Sanitization Demo")
    print("=" * 40)
    
    downloader = YouTubeDownloader()
    
    problematic_names = [
        "Video with / illegal \\ characters",
        "Video: with < many > illegal | chars?",
        "Video with \"quotes\" and *asterisks*",
        "   Video with spaces around   ",
        "Very" + "Long" * 50 + "VideoName",
    ]
    
    for original in problematic_names:
        sanitized = downloader.sanitize_filename(original)
        print(f"Original:  {original}")
        print(f"Sanitized: {sanitized}")
        print()


def demo_batch_file_creation():
    """Create a sample batch file"""
    print(f"{Fore.CYAN}📄 Sample URLs File Demo")
    print("=" * 40)
    
    sample_file = "demo_urls.txt"
    
    sample_content = """# Demo YouTube URLs File
# This is how you can prepare URLs for batch downloading

# Single videos (these are example URLs - replace with real ones):
# https://www.youtube.com/watch?v=dQw4w9WgXcQ
# https://youtu.be/jNQXAC9IVRw

# Playlists (these are example URLs - replace with real ones):
# https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M

# Mix of both:
# https://www.youtube.com/watch?v=ScMzIvxBSi4
# https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi

# To use this file:
# python batch_download.py demo_urls.txt
"""
    
    try:
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"✅ Created sample file: {sample_file}")
        print("You can edit this file and add real YouTube URLs")
        print(f"Then run: python batch_download.py {sample_file}")
        print()
        
    except Exception as e:
        print(f"❌ Error creating sample file: {e}")


def demo_subtitle_features():
    """Demonstrate subtitle download features"""
    print(f"{Fore.CYAN}📝 Subtitle Features Demo")
    print("=" * 40)
    
    print("The downloader supports multiple subtitle options:")
    print()
    
    print(f"{Fore.GREEN}✅ Available Features:")
    print("• Download English subtitles automatically")
    print("• Support for multiple subtitle formats (SRT, VTT)")
    print("• Option to embed subtitles in video files")
    print("• Option to keep subtitles as separate files")
    print("• Support for multiple languages")
    print("• Automatic and manual subtitle detection")
    print()
    
    print(f"{Fore.YELLOW}📋 Configuration Options:")
    print()
    
    print("1. Separate Subtitle Files (Default):")
    print("   downloader = YouTubeDownloader(download_subtitles=True, embed_subtitles=False)")
    print("   Result: video.mp4 + video.en.srt")
    print()
    
    print("2. Embedded Subtitles:")
    print("   downloader = YouTubeDownloader(download_subtitles=True, embed_subtitles=True)")
    print("   Result: video.mp4 (with built-in subtitles)")
    print()
    
    print("3. No Subtitles:")
    print("   downloader = YouTubeDownloader(download_subtitles=False)")
    print("   Result: video.mp4 (no subtitle files)")
    print()
    
    print("4. Multiple Languages:")
    print("   downloader = YouTubeDownloader(")
    print("       download_subtitles=True,")
    print("       subtitle_languages=['en', 'es', 'fr', 'de']")
    print("   )")
    print("   Result: video.mp4 + video.en.srt + video.es.srt + ...")
    print()
    
    print(f"{Fore.CYAN}🎮 Interface Support:")
    print("• GUI: Checkbox options for subtitle preferences")
    print("• CLI: Interactive prompts for subtitle settings") 
    print("• Batch: Command-line flags (--no-subtitles, --embed-subtitles)")
    print("• Code: Constructor parameters and configuration methods")
    print()


def demo_programmatic_usage():
    """Show how to use the downloader programmatically"""
    print(f"{Fore.CYAN}💻 Programmatic Usage Demo")
    print("=" * 40)
    
    code_example = '''
# Import the downloader
from youtube_downloader import YouTubeDownloader

# Basic usage with subtitles (default)
downloader = YouTubeDownloader(download_path="MyVideos")

# Custom subtitle settings
downloader_custom = YouTubeDownloader(
    download_path="MyVideos",
    download_subtitles=True,     # Download subtitles
    embed_subtitles=False,       # Keep as separate files
    subtitle_languages=['en', 'en-US', 'en-GB']  # English variants
)

# No subtitles
downloader_no_subs = YouTubeDownloader(
    download_path="MyVideos",
    download_subtitles=False
)

# Download a single video
success = downloader.download_url("https://www.youtube.com/watch?v=VIDEO_ID")

# Download a playlist
success = downloader.download_url("https://www.youtube.com/playlist?list=PLAYLIST_ID")

# Configure subtitles after creation
downloader.configure_subtitles(
    download_subtitles=True,
    embed_subtitles=True,  # Change to embedded subtitles
    subtitle_languages=['en', 'es', 'fr']  # Multiple languages
)

# Download multiple URLs
urls = [
    "https://www.youtube.com/watch?v=VIDEO1",
    "https://www.youtube.com/playlist?list=PLAYLIST1",
    "https://youtu.be/VIDEO2"
]

results = downloader.download_multiple_urls(urls)

# Check results
for url, success in results.items():
    print(f"{url}: {'Success' if success else 'Failed'}")
'''
    
    print("Here's how to use the downloader in your own code:")
    print(code_example)


def show_available_interfaces():
    """Show all available ways to use the downloader"""
    print(f"{Fore.CYAN}🎮 Available Interfaces")
    print("=" * 40)
    
    interfaces = [
        ("python youtube_downloader.py", "Interactive command-line interface"),
        ("python gui.py", "Graphical user interface (easiest)"),
        ("python batch_download.py urls.txt", "Batch processing from file"),
        ("run.bat", "Windows menu launcher (Windows only)"),
        ("python examples.py", "Interactive examples"),
    ]
    
    for command, description in interfaces:
        print(f"• {command}")
        print(f"  └─ {description}")
        print()


def main():
    """Run all demos"""
    print(f"{Fore.MAGENTA}🎬 YouTube Downloader - Feature Demo")
    print("=" * 60)
    print()
    
    print(f"{Fore.YELLOW}This demo shows the features of the YouTube downloader")
    print(f"{Fore.YELLOW}without actually downloading any videos.")
    print()
    
    # Run demos
    demo_url_detection()
    print()
    
    demo_folder_structure()
    print()
    
    demo_subtitle_features()
    print()
    
    demo_filename_sanitization()
    print()
    
    demo_batch_file_creation()
    print()
    
    demo_programmatic_usage()
    print()
    
    show_available_interfaces()
    print()
    
    print(f"{Fore.GREEN}✅ Demo completed!")
    print()
    print(f"{Fore.CYAN}Ready to start downloading? Try:")
    print(f"{Fore.WHITE}• python youtube_downloader.py  {Fore.CYAN}(for interactive mode)")
    print(f"{Fore.WHITE}• python gui.py                {Fore.CYAN}(for graphical interface)")
    print(f"{Fore.WHITE}• run.bat                      {Fore.CYAN}(for Windows menu)")
    print()
    print(f"{Fore.YELLOW}Remember: Always respect YouTube's Terms of Service!")


if __name__ == "__main__":
    main()
