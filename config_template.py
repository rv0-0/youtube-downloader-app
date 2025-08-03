# YouTube Downloader Configuration
# Copy this file to config.py and modify as needed

# Default download directory
DEFAULT_DOWNLOAD_PATH = "Downloads"

# Video quality settings
# Options: 'best', 'worst', 'best[height<=720]', 'best[height<=1080]', etc.
VIDEO_QUALITY = 'best[height<=1080]'

# Audio quality for audio-only downloads
# Options: 'best', 'worst', '320', '256', '192', '128', etc.
AUDIO_QUALITY = 'best'

# Output filename template for single videos
# Available variables: %(title)s, %(uploader)s, %(upload_date)s, %(duration)s, etc.
SINGLE_VIDEO_TEMPLATE = '%(title)s.%(ext)s'

# Output filename template for playlist videos
# Available variables: %(playlist_index)s, %(title)s, %(uploader)s, etc.
PLAYLIST_VIDEO_TEMPLATE = '%(playlist_index)02d - %(title)s.%(ext)s'

# Whether to restrict filenames to ASCII characters
RESTRICT_FILENAMES = True

# Whether to download subtitles
DOWNLOAD_SUBTITLES = False

# Whether to download automatic subtitles
DOWNLOAD_AUTO_SUBTITLES = False

# Subtitle languages (if downloading subtitles)
# Examples: ['en'], ['en', 'es', 'fr'], ['all']
SUBTITLE_LANGUAGES = ['en']

# Whether to embed subtitles in video file (if supported)
EMBED_SUBTITLES = False

# Whether to download video description
WRITE_DESCRIPTION = False

# Whether to download video annotations
WRITE_ANNOTATIONS = False

# Whether to download video info JSON
WRITE_INFO_JSON = False

# Whether to download video thumbnail
WRITE_THUMBNAIL = False

# Maximum number of concurrent downloads
MAX_CONCURRENT_DOWNLOADS = 1

# Sleep interval between downloads (seconds)
SLEEP_INTERVAL = 1

# Retry attempts for failed downloads
MAX_RETRIES = 3

# Whether to continue downloading other videos if one fails
CONTINUE_ON_ERROR = True

# Custom user agent string (optional)
USER_AGENT = None

# Proxy settings (optional)
# Example: 'http://proxy.example.com:8080'
PROXY = None

# Cookies file path (optional)
# Use this if you need to access age-restricted or private content
COOKIES_FILE = None

# Archive file to record downloaded video IDs
# This prevents re-downloading the same video
ARCHIVE_FILE = None

# Age limit for videos (skip videos marked for older audiences)
AGE_LIMIT = None

# Whether to skip videos that are live streams
SKIP_LIVE_STREAMS = True

# Whether to skip videos that are premieres
SKIP_PREMIERES = False

# Minimum video duration (in seconds) - skip shorter videos
MIN_DURATION = None

# Maximum video duration (in seconds) - skip longer videos
MAX_DURATION = None

# Date range settings
# Format: YYYYMMDD
DATE_BEFORE = None  # Only download videos uploaded before this date
DATE_AFTER = None   # Only download videos uploaded after this date

# Whether to use external downloader (like aria2c, axel, etc.)
EXTERNAL_DOWNLOADER = None

# External downloader arguments
EXTERNAL_DOWNLOADER_ARGS = None

# Whether to keep original video files when post-processing
KEEP_VIDEO = True

# Post-processing options
POST_PROCESSORS = [
    # Example: Convert to MP3
    # {
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'mp3',
    #     'preferredquality': '192',
    # },
    
    # Example: Add metadata
    # {
    #     'key': 'FFmpegMetadata',
    # },
    
    # Example: Embed thumbnail
    # {
    #     'key': 'EmbedThumbnail',
    # },
]
