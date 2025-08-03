# How to Run the YouTube Downloader

## 📋 Prerequisites

1. **Python 3.7+** installed on your system
2. **FFmpeg** installed (for best quality video/audio merging)
3. **Dependencies** installed from requirements.txt

## 🚀 Quick Start

### Method 1: Run the GUI (Recommended) ✅
```bash
# Navigate to the project directory
cd "C:\Users\RAVI\Documents\MyProject\youtube-downloader-app"

# Run the GUI application (now with modular architecture)
python gui.py
```

### Method 2: Use the launcher menu ⭐
```bash
# Run the comprehensive launcher
run.bat
# Select option 2 for GUI
```

### Method 2: Run from command line
```bash
# For single video
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# For playlist
python youtube_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Method 3: Use the demo script
```bash
python demo.py
```

### Method 4: Batch download
```bash
python batch_download.py
```

## 🎛️ GUI Usage

1. **Launch the GUI**: `python gui.py`
2. **Set download path**: Click "Browse" to choose where to save videos
3. **Select quality**: Choose from the dropdown menu:
   - Best Quality (4K/1440p/1080p) - Recommended
   - High Quality (1080p max)
   - Medium Quality (720p max)
   - Low Quality (480p max)
   - Premium Quality (VP9+Opus)
   - Ultra Quality (AV1+Opus)
   - Audio Only (Best)
   - Custom Format (advanced users)
4. **Configure subtitles**: 
   - Check "Subtitles" to download English subtitles
   - Check "Embed" to embed subtitles into video files
5. **Add URLs**: Paste YouTube URLs (one per line) in the text area
6. **Start download**: Click "🚀 Start Download"
7. **Monitor progress**: Watch individual video progress and overall completion
8. **Stop if needed**: Click "⏹️ Stop" to cancel downloads

## 📁 Modular Code Structure

The GUI has been refactored into modular components:

```
gui/
├── __init__.py           # Package initialization
├── constants.py          # Configuration constants
├── ui_components.py      # UI widget creation
├── progress_tracker.py   # Progress tracking logic
├── download_manager.py   # Download processes & threading
└── main_window.py        # Main window coordination
```

### Running Individual Components

```bash
# Test specific modules
python -c "from gui.constants import QUALITY_OPTIONS; print(QUALITY_OPTIONS)"
python -c "from gui.main_window import YouTubeDownloaderGUI; print('GUI ready')"
```

## 🔧 Advanced Usage

### Command Line Options
```bash
# The YouTube downloader supports direct URL arguments
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# For playlists
python youtube_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Note: Advanced options are set programmatically
```

### Programmatic Usage
```python
from youtube_downloader import YouTubeDownloader

# Create downloader instance (CORRECTED PARAMETERS)
downloader = YouTubeDownloader(
    download_path="Downloads",  # Correct parameter name
    download_subtitles=True,
    embed_subtitles=False
)

# Download single video (CORRECTED METHOD NAME)
success = downloader.download_single_video("https://www.youtube.com/watch?v=VIDEO_ID")

# Download playlist (CORRECTED METHOD NAME)
success = downloader.download_playlist("https://www.youtube.com/playlist?list=PLAYLIST_ID")

# Or use the auto-detect method
success = downloader.download_url("https://www.youtube.com/watch?v=VIDEO_ID")
```

## 🛠️ Troubleshooting

### Common Issues

1. **"yt-dlp not found"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"YouTubeDownloader.__init__() got an unexpected keyword argument"**
   - ✅ **FIXED**: This was resolved in the modular refactoring
   - The download manager now uses the correct parameter names

3. **"FFmpeg not found"**
   - Install FFmpeg from https://ffmpeg.org/
   - Add to system PATH

4. **"Permission denied"**
   - Check download folder permissions
   - Run as administrator if needed

5. **"Private video" errors**
   - Some playlist videos may be private/deleted
   - The app will skip these and continue

6. **Audio missing from high-quality videos**
   - Ensure FFmpeg is installed
   - Use "Best Quality" format for automatic merging

### Debug Mode
```bash
# Run with debug logging
python gui.py --debug
```

## 📊 Features

✅ **Single video & playlist support**  
✅ **Quality selection (4K to 480p)**  
✅ **English subtitle download**  
✅ **Progress tracking per video**  
✅ **Robust error handling**  
✅ **Process management (stop downloads)**  
✅ **FFmpeg integration for best quality**  
✅ **Modular, maintainable code**

## 🎯 Best Practices

1. **Use "Best Quality" option** for optimal results
2. **Enable subtitles** for accessibility
3. **Choose appropriate download folder** with sufficient space
4. **Monitor progress** especially for large playlists
5. **Check logs** if downloads fail

## 📝 File Organization

Downloaded files are organized as:
```
Downloads/
├── VideoTitle1.webm
├── VideoTitle1.en.vtt
├── VideoTitle2.mp4
└── VideoTitle2.en.vtt
```

For playlists, videos are numbered sequentially for proper ordering.

---

**Need help?** Check the troubleshooting guide or review the logs in the GUI for detailed error information.
