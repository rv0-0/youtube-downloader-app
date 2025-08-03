#!/usr/bin/env python3
"""
Batch processing script for YouTube Downloader
Processes URLs from a text file
"""

import sys
import argparse
from pathlib import Path
from youtube_downloader import YouTubeDownloader
from colorama import Fore, init

init(autoreset=True)


def read_urls_from_file(file_path: str) -> list:
    """
    Read URLs from a text file (one URL per line)
    
    Args:
        file_path (str): Path to the text file containing URLs
        
    Returns:
        list: List of valid YouTube URLs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urls = []
            for line_num, line in enumerate(file, 1):
                url = line.strip()
                
                # Skip empty lines and comments
                if not url or url.startswith('#'):
                    continue
                
                # Validate YouTube URL
                if 'youtube.com' in url or 'youtu.be' in url:
                    urls.append(url)
                else:
                    print(f"{Fore.YELLOW}Warning: Line {line_num} - Invalid YouTube URL: {url}")
            
            return urls
    
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found: {file_path}")
        return []
    except Exception as e:
        print(f"{Fore.RED}Error reading file: {e}")
        return []


def create_sample_urls_file(file_path: str):
    """
    Create a sample URLs file with examples
    
    Args:
        file_path (str): Path where to create the sample file
    """
    sample_content = """# YouTube Downloader - URLs File
# Add one YouTube URL per line
# Lines starting with # are comments and will be ignored
# Empty lines are also ignored

# Example single video (replace with actual URLs):
# https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Example playlist (replace with actual URLs):
# https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M

# Example short URL:
# https://youtu.be/dQw4w9WgXcQ

# Add your URLs below:

"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(sample_content)
        print(f"{Fore.GREEN}Sample URLs file created: {file_path}")
        print(f"{Fore.YELLOW}Edit this file and add your YouTube URLs, then run the batch processor again.")
    except Exception as e:
        print(f"{Fore.RED}Error creating sample file: {e}")


def main():
    """Main function for batch processing"""
    parser = argparse.ArgumentParser(
        description="Batch YouTube Downloader - Process URLs from a file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s urls.txt                    # Download from urls.txt to default folder
  %(prog)s urls.txt -o MyDownloads     # Download to MyDownloads folder
  %(prog)s --create-sample urls.txt    # Create a sample URLs file
  
File format:
  - One URL per line
  - Lines starting with # are comments
  - Empty lines are ignored
  - Supports both video and playlist URLs
        """
    )
    
    parser.add_argument('file', nargs='?', help='Text file containing YouTube URLs (one per line)')
    parser.add_argument('-o', '--output', default='Downloads', 
                       help='Output directory for downloads (default: Downloads)')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create a sample URLs file and exit')
    parser.add_argument('--no-subtitles', action='store_true',
                       help='Skip downloading subtitles')
    parser.add_argument('--embed-subtitles', action='store_true',
                       help='Embed subtitles in video files instead of separate files')
    
    args = parser.parse_args()
    
    # Handle sample file creation
    if args.create_sample:
        if not args.file:
            print(f"{Fore.RED}Error: Please specify a filename for the sample file")
            print(f"{Fore.YELLOW}Example: {sys.argv[0]} --create-sample urls.txt")
            return 1
        
        create_sample_urls_file(args.file)
        return 0
    
    # Validate arguments
    if not args.file:
        parser.print_help()
        return 1
    
    # Check if file exists
    if not Path(args.file).exists():
        print(f"{Fore.RED}Error: File not found: {args.file}")
        print(f"{Fore.YELLOW}Tip: Use --create-sample to create a sample file")
        return 1
    
    print(f"{Fore.CYAN}🎬 YouTube Downloader - Batch Mode")
    print("=" * 50)
    print(f"{Fore.BLUE}Input file: {args.file}")
    print(f"{Fore.BLUE}Output directory: {args.output}")
    print()
    
    # Read URLs from file
    print(f"{Fore.YELLOW}Reading URLs from file...")
    urls = read_urls_from_file(args.file)
    
    if not urls:
        print(f"{Fore.RED}No valid YouTube URLs found in the file")
        return 1
    
    print(f"{Fore.GREEN}Found {len(urls)} valid YouTube URLs")
    
    # Configure subtitle settings
    download_subtitles = not args.no_subtitles
    embed_subtitles = args.embed_subtitles
    
    print(f"{Fore.BLUE}Subtitle settings:")
    print(f"  Download subtitles: {'Yes' if download_subtitles else 'No'}")
    if download_subtitles:
        print(f"  Embed subtitles: {'Yes' if embed_subtitles else 'No (separate files)'}")
    print()
    
    # Create downloader and process URLs
    try:
        downloader = YouTubeDownloader(
            download_path=args.output,
            download_subtitles=download_subtitles,
            embed_subtitles=embed_subtitles
        )
        results = downloader.download_multiple_urls(urls)
        
        # Print final summary
        successful = sum(1 for success in results.values() if success)
        failed = len(urls) - successful
        
        print(f"\n{Fore.CYAN}Final Summary:")
        print(f"{Fore.GREEN}Successfully processed: {successful}/{len(urls)}")
        
        if failed > 0:
            print(f"{Fore.RED}Failed: {failed}")
            return 1
        else:
            print(f"{Fore.GREEN}All downloads completed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Batch processing interrupted by user")
        return 1
    except Exception as e:
        print(f"{Fore.RED}Error during batch processing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
