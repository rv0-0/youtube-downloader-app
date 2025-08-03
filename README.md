# YouTube Downloader

A powerful YouTube downloader that can handle both individual videos and entire playlists with intelligent organization.

## 🆕 Latest Updates

- **Fixed HTTP 403 Forbidden errors** with updated yt-dlp version
- **Added Enhanced Downloader** with multiple fallback strategies  
- **Improved error handling** for problematic videos and playlists
- **Better retry mechanisms** for network issues
- **Audio-only fallback** for severely restricted content

## Features

- Download individual YouTube videos in highest quality
- Download entire playlists with proper folder organization
- Automatic detection of playlist vs single video links
- Sequential numbering for playlist videos (01, 02, 03...)
- Folder creation with playlist names
- **📝 English subtitle download support**
- **🎛️ Configurable subtitle options (separate .srt files or embedded)**
- **🌍 Multi-language subtitle support**
- Progress tracking and error handling
- Support for multiple URLs at once
- **NEW: Enhanced downloader with fallback strategies**
- **NEW: Better handling of restricted content**

## Requirements

- Python 3.7+
- yt-dlp (latest version)
- requests
- colorama

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Or run the setup script:
   ```
   python setup.py
   ```

## Usage

### � Subtitle Options

The downloader supports English subtitle download with flexible configuration:

**Default behavior**: Downloads English subtitles as separate .srt files
```python
downloader = YouTubeDownloader()  # Subtitles enabled by default
```

**Custom subtitle settings**:
```python
# Separate subtitle files (recommended)
downloader = YouTubeDownloader(
    download_subtitles=True,
    embed_subtitles=False  # Creates .srt files alongside videos
)

# Embedded subtitles 
downloader = YouTubeDownloader(
    download_subtitles=True,
    embed_subtitles=True  # Embeds subtitles in video file
)

# No subtitles
downloader = YouTubeDownloader(download_subtitles=False)

# Multiple languages
downloader = YouTubeDownloader(
    subtitle_languages=['en', 'es', 'fr', 'de']
)
```

### �🚀 Quick Start (Recommended for problematic videos)
```bash
python enhanced_downloader.py
```
This version includes multiple fallback strategies for handling restricted or problematic content.

### Standard GUI Interface
```bash
python gui.py
```

### Command Line Interface
```bash
python youtube_downloader.py
```

### Batch Processing
```bash
python batch_download.py urls.txt
```

### Windows Menu (Windows only)
```bash
run.bat
```

## 🛠️ Troubleshooting

If you encounter issues like "HTTP 403 Forbidden" or download failures:

1. **Use the Enhanced Downloader**: `python enhanced_downloader.py`
2. **Update yt-dlp**: `pip install --upgrade yt-dlp`
3. **Check the troubleshooting guide**: See `TROUBLESHOOTING.md`
4. **Try different URLs**: Some videos may be restricted

### Common Issues and Quick Fixes

- **403 Forbidden errors**: Use `enhanced_downloader.py`
- **Age-restricted content**: Enhanced downloader tries audio-only fallback
- **Playlist failures**: Enhanced version downloads videos individually
- **Network timeouts**: Automatic retries with increasing delays

## Supported URL Formats

- Single videos: `https://www.youtube.com/watch?v=VIDEO_ID`
- Playlists: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- And more YouTube URL formats

## Output Structure

```
Downloads/
├── Single Videos/
│   ├── Video Title 1.mp4
│   ├── Video Title 1.en.srt        # English subtitles
│   ├── Video Title 2.mp4
│   └── Video Title 2.en.srt
└── Playlists/
    └── Playlist Name/
        ├── 01 - First Video.mp4
        ├── 01 - First Video.en.srt
        ├── 02 - Second Video.mp4
        ├── 02 - Second Video.en.srt
        ├── 03 - Third Video.mp4
        └── 03 - Third Video.en.srt
```

**Note**: Subtitle files (.srt) are created when subtitle download is enabled (default behavior).

## License

This project is for educational purposes only. Please respect YouTube's Terms of Service.
