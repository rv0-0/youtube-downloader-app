# Quick Start Guide

## 🚀 Getting Started

### 1. Setup
First, run the setup script to install dependencies:
```bash
python setup.py
```

### 2. Basic Usage

#### Option A: GUI Interface (Easiest)
```bash
python gui.py
```
- Simple graphical interface
- Paste URLs and click download
- Progress tracking and logs

#### Option B: Command Line Interface
```bash
python youtube_downloader.py
```
- Interactive command-line interface
- Enter URLs one by one
- Real-time feedback

#### Option C: Windows Launcher (Windows only)
```bash
run.bat
```
- Menu-driven interface
- Access all features easily

### 3. Features Overview

| Feature | Single Videos | Playlists |
|---------|---------------|-----------|
| Auto-detection | ✅ | ✅ |
| Quality selection | ✅ Best (1080p) | ✅ Best (1080p) |
| **English subtitles** | ✅ `.srt` files | ✅ `.srt` files |
| **Subtitle options** | ✅ Separate/Embedded | ✅ Separate/Embedded |
| Folder organization | `Downloads/Single Videos/` | `Downloads/Playlists/[Name]/` |
| File naming | `Video Title.ext` | `01 - Video Title.ext` |
| Progress tracking | ✅ | ✅ |
| Error handling | ✅ | ✅ |

### 4. Folder Structure
```
Downloads/
├── Single Videos/
│   ├── Amazing Video.mp4
│   ├── Amazing Video.en.srt          # English subtitles
│   ├── Another Video.mp4
│   └── Another Video.en.srt
└── Playlists/
    ├── My Playlist/
    │   ├── 01 - First Video.mp4
    │   ├── 01 - First Video.en.srt
    │   ├── 02 - Second Video.mp4
    │   ├── 02 - Second Video.en.srt
    │   ├── 03 - Third Video.mp4
    │   └── 03 - Third Video.en.srt
    └── Another Playlist/
        ├── 01 - Video One.mp4
        ├── 01 - Video One.en.srt
        ├── 02 - Video Two.mp4
        └── 02 - Video Two.en.srt
```

### 5. URL Types Supported

✅ **Single Videos:**
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

✅ **Playlists:**
- `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`

### 6. Batch Processing

Create a text file with URLs:
```bash
# Create sample file
python batch_download.py --create-sample my_urls.txt

# Edit the file with your URLs, then:
python batch_download.py my_urls.txt
```

### 7. Subtitle Configuration

**📝 Quick Subtitle Options:**

**GUI Interface**: Check/uncheck subtitle options in the interface
- "Download English subtitles" - Creates .srt files
- "Embed subtitles in video" - Builds subtitles into video file

**Command Line**: Answer prompts when starting
```bash
python youtube_downloader.py
# Follow prompts for subtitle preferences
```

**Batch Processing**: Use command-line flags
```bash
# Download without subtitles
python batch_download.py urls.txt --no-subtitles

# Download with embedded subtitles
python batch_download.py urls.txt --embed-subtitles
```

**Programmatic**: Configure in code
```python
# Default: separate subtitle files
downloader = YouTubeDownloader()

# Custom subtitle settings
downloader = YouTubeDownloader(
    download_subtitles=True,    # Download subtitles
    embed_subtitles=False,      # Separate .srt files
    subtitle_languages=['en']   # English only
)
```

### 8. Troubleshooting

**Dependencies not installed?**
```bash
pip install -r requirements.txt
```

**Permission errors?**
- Run as administrator (Windows)
- Check folder permissions

**Download failures?**
- Check internet connection
- Verify URL is valid
- Some videos may be restricted

### 9. Examples

```python
from youtube_downloader import YouTubeDownloader

# Create downloader
downloader = YouTubeDownloader("MyDownloads")

# Download single video
downloader.download_url("https://www.youtube.com/watch?v=VIDEO_ID")

# Download playlist
downloader.download_url("https://www.youtube.com/playlist?list=PLAYLIST_ID")

# Download multiple URLs
urls = [
    "https://www.youtube.com/watch?v=VIDEO1",
    "https://www.youtube.com/playlist?list=PLAYLIST1"
]
results = downloader.download_multiple_urls(urls)
```

## 🎯 Most Common Use Cases

1. **Download a few videos:** Use the GUI (`python gui.py`)
2. **Download many URLs:** Use batch mode with a text file
3. **Download regularly:** Use the command line interface
4. **Integrate with code:** Import the YouTubeDownloader class

## ⚠️ Important Notes

- Respect YouTube's Terms of Service
- Don't download copyrighted content without permission
- Use responsibly and ethically
- Some videos may be geo-restricted or age-gated

## 🆘 Need Help?

1. Check the README.md for detailed documentation
2. Run tests: `python test_downloader.py`
3. Look at examples: `python examples.py`
4. Check configuration: `config_template.py`
