# Troubleshooting Guide for YouTube Downloader

## 🚨 Common Issues and Solutions

### 1. HTTP 403 Forbidden Errors

**Problem:** You see errors like "HTTP Error 403: Forbidden" or "unable to download video data"

**Causes:**
- Age-restricted content
- Region-blocked videos
- Videos requiring login
- YouTube anti-bot measures
- Outdated yt-dlp version

**Solutions:**

#### A. Update yt-dlp to latest version
```bash
pip install --upgrade yt-dlp
```

#### B. Use the Enhanced Downloader
```bash
python enhanced_downloader.py
```
This version includes multiple fallback strategies.

#### C. Try different quality settings
Edit your config to use lower quality:
```python
# In youtube_downloader.py, change format to:
'format': 'worst[height>=480]/worst'
```

#### D. Add delays between downloads
```python
# Increase sleep intervals
'sleep_interval': 2,
'max_sleep_interval': 10,
```

### 2. Incomplete Data Received Warnings

**Problem:** Warnings like "Incomplete data received. Retrying (1/3)..."

**Causes:**
- YouTube API rate limiting
- Network connectivity issues
- Server overload

**Solutions:**

#### A. Increase retry counts
```python
'retries': 5,
'fragment_retries': 5,
'extractor_retries': 5,
```

#### B. Add longer delays
```python
'sleep_interval': 3,
'max_sleep_interval': 15,
```

#### C. Use the enhanced downloader with fallback strategies

### 3. Age-Restricted Content

**Problem:** Cannot download age-restricted videos

**Solutions:**

#### A. Use cookies (if you're logged in to YouTube)
1. Install browser_cookie3: `pip install browser_cookie3`
2. Add to downloader options:
```python
'cookiefile': 'cookies.txt',  # Export cookies from browser
```

#### B. Try the audio-only fallback
The enhanced downloader automatically tries audio-only for problematic videos.

### 4. Regional Restrictions

**Problem:** "Video not available in your country"

**Solutions:**

#### A. Use a VPN or proxy
```python
'proxy': 'http://proxy-server:port',
```

#### B. Try different formats
```python
'format': 'best[height<=720]/worst',
```

### 5. Playlist Issues

**Problem:** Some videos in playlist fail to download

**Solutions:**

#### A. Use Enhanced Downloader
The enhanced version downloads videos individually with better error handling.

#### B. Enable ignore errors for playlists
```python
'ignoreerrors': True,
'continue_dl': True,
```

#### C. Skip unavailable videos
```python
'skip_unavailable_fragments': True,
```

### 6. Memory or Performance Issues

**Problem:** Downloads are slow or cause system issues

**Solutions:**

#### A. Limit concurrent downloads
```python
'concurrent_fragment_downloads': 1,
```

#### B. Use external downloader
```python
'external_downloader': 'aria2c',
'external_downloader_args': ['-j', '4', '-s', '4'],
```

#### C. Download lower quality
```python
'format': 'best[height<=480]/worst',
```

## 🛠️ Advanced Troubleshooting

### Check yt-dlp Version
```bash
yt-dlp --version
```

### Test with yt-dlp directly
```bash
yt-dlp "YOUR_URL_HERE" --verbose
```

### Enable debug mode in the downloader
```python
'verbose': True,
'debug_printtraffic': True,
```

### Export detailed logs
```python
'writeinfojson': True,
'writedescription': True,
```

## 🔧 Configuration Options

### For Problematic Videos
```python
problematic_opts = {
    'format': 'worst[height>=360]/worst',
    'retries': 10,
    'fragment_retries': 10,
    'sleep_interval': 3,
    'max_sleep_interval': 15,
    'ignoreerrors': True,
    'no_warnings': False,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}
```

### For Stable Downloads
```python
stable_opts = {
    'format': 'best[height<=720]/best',
    'retries': 3,
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'ignoreerrors': False,
}
```

## 🆘 When All Else Fails

### 1. Try Alternative URLs
- Use `youtu.be/VIDEO_ID` instead of full YouTube URLs
- Try the mobile URL format
- Check if the video is available on different YouTube domains

### 2. Use Different Tools
- Try downloading with the command-line yt-dlp directly
- Use browser extensions as alternatives
- Consider other download tools

### 3. Check Video Status
- Verify the video is still public
- Check if it's available in your region
- Ensure it's not age-restricted

### 4. Update Everything
```bash
pip install --upgrade yt-dlp requests colorama
```

### 5. Clear Cache
Delete the yt-dlp cache folder:
- Windows: `%APPDATA%\yt-dlp`
- Linux/Mac: `~/.cache/yt-dlp`

## 📞 Getting Help

1. **Check the logs** - The downloader provides detailed error messages
2. **Try the enhanced downloader** - `python enhanced_downloader.py`
3. **Test individual URLs** - Isolate problematic videos
4. **Check yt-dlp GitHub issues** - https://github.com/yt-dlp/yt-dlp/issues
5. **Verify YouTube ToS compliance** - Ensure ethical usage

## ⚠️ Important Notes

- **Respect YouTube's Terms of Service**
- **Don't download copyrighted content without permission**
- **Some restrictions are intentional** (age gates, regional blocks)
- **YouTube constantly changes their systems** - what works today may not work tomorrow
- **Always keep yt-dlp updated** - newer versions handle YouTube changes better

## 🔄 Quick Fixes Checklist

- [ ] Updated yt-dlp to latest version
- [ ] Tried the enhanced downloader
- [ ] Checked if video is publicly accessible
- [ ] Verified URL format is correct
- [ ] Tested with a simple, unrestricted video first
- [ ] Checked network connection
- [ ] Tried lower quality format
- [ ] Added delays between downloads
- [ ] Enabled error ignoring for playlists
