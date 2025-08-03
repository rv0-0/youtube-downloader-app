# 📝 Subtitle Feature Documentation

## Overview

The YouTube Downloader now includes comprehensive English subtitle support with flexible configuration options. This feature automatically downloads subtitles alongside videos and provides multiple ways to handle them.

## 🎯 Key Features

### ✅ What's Included
- **Automatic English subtitle detection and download**
- **Support for multiple subtitle formats** (SRT, VTT, and others)
- **Configurable subtitle handling** (separate files or embedded)
- **Multi-language support** (English variants and other languages)
- **Manual and automatic subtitle detection**
- **Integration across all interfaces** (GUI, CLI, batch, programmatic)

### 📁 File Organization
When subtitles are downloaded, they are organized alongside the video files:

```
Downloads/
├── Single Videos/
│   ├── Video Title.mp4
│   └── Video Title.en.srt        # English subtitle file
└── Playlists/
    └── Playlist Name/
        ├── 01 - Video Title.mp4
        └── 01 - Video Title.en.srt   # Numbered subtitle file
```

## 🔧 Configuration Options

### 1. Default Behavior (Recommended)
```python
downloader = YouTubeDownloader()
# Downloads subtitles as separate .srt files
```

### 2. Separate Subtitle Files
```python
downloader = YouTubeDownloader(
    download_subtitles=True,
    embed_subtitles=False  # Creates .srt files alongside videos
)
```
**Result**: `video.mp4` + `video.en.srt`

### 3. Embedded Subtitles
```python
downloader = YouTubeDownloader(
    download_subtitles=True,
    embed_subtitles=True   # Embeds subtitles in video file
)
```
**Result**: `video.mp4` (with built-in subtitles)

### 4. No Subtitles
```python
downloader = YouTubeDownloader(download_subtitles=False)
```
**Result**: `video.mp4` (no subtitle files)

### 5. Multiple Languages
```python
downloader = YouTubeDownloader(
    download_subtitles=True,
    subtitle_languages=['en', 'es', 'fr', 'de']  # English, Spanish, French, German
)
```
**Result**: `video.mp4` + `video.en.srt` + `video.es.srt` + ...

### 6. Runtime Configuration
```python
downloader = YouTubeDownloader()

# Change settings after creation
downloader.configure_subtitles(
    download_subtitles=True,
    embed_subtitles=True,
    subtitle_languages=['en', 'es']
)
```

## 🎮 Interface Usage

### GUI Interface (`python gui.py`)
- **"Download English subtitles"** checkbox - Enable/disable subtitle download
- **"Embed subtitles in video"** checkbox - Choose between separate files or embedded

### Command Line Interface (`python youtube_downloader.py`)
Interactive prompts for subtitle preferences:
```
Download English subtitles? (y/n, default: y): y
Embed subtitles in video file? (y/n, default: n): n
```

### Batch Processing (`python batch_download.py`)
Command-line flags for subtitle control:
```bash
# Download without subtitles
python batch_download.py urls.txt --no-subtitles

# Download with embedded subtitles
python batch_download.py urls.txt --embed-subtitles

# Normal download (with separate subtitle files)
python batch_download.py urls.txt
```

## 📋 Subtitle Language Codes

### English Variants (Default)
- `en` - Generic English
- `en-US` - US English
- `en-GB` - British English
- `en.*` - All English variants

### Popular Languages
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese

## 🛠️ Technical Details

### Subtitle Formats Supported
1. **SRT** (SubRip) - Most compatible, recommended
2. **VTT** (WebVTT) - Web standard
3. **Best available** - Automatic format selection

### Download Priority
1. **Manual subtitles** (human-created) - Preferred when available
2. **Automatic subtitles** (AI-generated) - Fallback option
3. **No subtitles** - Continues download without subtitles if none available

### Error Handling
- **Missing subtitles**: Downloads continue without subtitles
- **Format issues**: Automatic fallback to available formats
- **Language unavailable**: Downloads available languages only

## 💡 Best Practices

### Recommended Settings for Most Users
```python
downloader = YouTubeDownloader(
    download_subtitles=True,    # Enable subtitle download
    embed_subtitles=False,      # Keep as separate .srt files
    subtitle_languages=['en']   # English only for simplicity
)
```

### Why Separate Files Are Recommended
- **Compatibility**: .srt files work with all video players
- **Editability**: Easy to modify or translate
- **Portability**: Can be used with different video files
- **Storage**: Smaller file sizes

### When to Use Embedded Subtitles
- **Single file preference**: Want everything in one file
- **Sharing**: Easier to share one file with built-in subtitles
- **Streaming**: Some platforms prefer embedded subtitles

## 🔍 Troubleshooting

### Subtitles Not Downloading
1. **Check if video has subtitles**: Not all videos have subtitles available
2. **Language availability**: Requested language might not exist
3. **Network issues**: Subtitle download might fail while video succeeds

### Subtitle Quality
- **Manual vs Auto**: Manual subtitles are higher quality than auto-generated
- **Language variants**: Try different English variants (en, en-US, en-GB)
- **Fallback**: System tries multiple formats automatically

### File Issues
- **Missing .srt files**: Check if `download_subtitles=True`
- **Embedded not working**: Some video formats don't support embedding
- **Encoding issues**: Use UTF-8 compatible players

## 📈 Examples

### Quick Test
```python
from youtube_downloader import YouTubeDownloader

# Test with a public video (replace URL)
downloader = YouTubeDownloader("test_downloads")
success = downloader.download_url("YOUR_YOUTUBE_URL_HERE")

# Check results in test_downloads folder
```

### Production Usage
```python
# Configure for your needs
downloader = YouTubeDownloader(
    download_path="My_Videos",
    download_subtitles=True,
    embed_subtitles=False,
    subtitle_languages=['en', 'es']  # English and Spanish
)

# Process multiple URLs
urls = ["url1", "url2", "url3"]
results = downloader.download_multiple_urls(urls)
```

## 🚀 What's New

This subtitle feature adds:
- ✅ **English subtitle download by default**
- ✅ **Configurable subtitle options across all interfaces**
- ✅ **Support for multiple languages**
- ✅ **Choice between separate files and embedded subtitles**
- ✅ **Proper file organization with subtitles**
- ✅ **Error handling for missing subtitles**
- ✅ **Backward compatibility** (existing code continues to work)

The feature is enabled by default but can be easily disabled or customized based on your needs!
