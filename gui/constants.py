"""
Constants and configuration for the YouTube Downloader GUI
"""

# Quality options - Updated for proper audio+video merging with ffmpeg
QUALITY_OPTIONS = {
    "Best Quality (4K/1440p/1080p)": "bv*+ba/b",
    "High Quality (1080p max)": "bv*[height<=1080]+ba/b[height<=1080]",
    "Medium Quality (720p max)": "bv*[height<=720]+ba/b[height<=720]", 
    "Low Quality (480p max)": "bv*[height<=480]+ba/b[height<=480]",
    "Premium Quality (VP9+Opus)": "bv*[vcodec^=vp9]+ba[acodec^=opus]/bv*+ba/b",
    "Ultra Quality (AV1+Opus)": "bv*[vcodec^=av01]+ba[acodec^=opus]/bv*+ba/b",
    "Audio Only (Best)": "ba[ext=m4a]/ba[ext=mp3]/ba/b",
    "Custom Format": "custom"
}

# Default GUI settings
DEFAULT_WINDOW_SIZE = "800x650"
DEFAULT_MIN_SIZE = (700, 500)
DEFAULT_DOWNLOAD_PATH = "Downloads"
DEFAULT_CUSTOM_FORMAT = "bv*+ba/b"

# Window styling
MAIN_BG_COLOR = '#f8f9fa'
SECONDARY_BG_COLOR = '#f0f0f0'

# Font settings
TITLE_FONT = ("Segoe UI", 14, "bold")
NORMAL_FONT = ("Segoe UI", 9)
BOLD_FONT = ("Segoe UI", 9, "bold")
CODE_FONT = ("Consolas", 8)
URL_FONT = ("Consolas", 9)

# Progress tree columns
PROGRESS_COLUMNS = ("Index", "Title", "Status", "Progress")
PROGRESS_COLUMN_WIDTHS = {
    "Index": 40,
    "Title": 300,
    "Status": 100,
    "Progress": 80
}

# Help text for format strings
FORMAT_HELP_TEXT = """🎥 Custom Format Examples:

🏆 BEST QUALITY (With FFmpeg):
• bv*+ba/b - Best video + audio (recommended)
• bv*[ext=mp4]+ba[ext=m4a]/b - MP4 video + M4A audio
• bv*[vcodec^=vp9]+ba[acodec^=opus]/bv*+ba - VP9 + Opus

📺 RESOLUTION LIMITS:
• bv*[height<=1080]+ba/b[height<=1080] - Max 1080p
• bv*[height<=720]+ba/b[height<=720] - Max 720p

🎵 AUDIO ONLY:
• ba[ext=m4a]/ba - M4A audio
• ba[ext=mp3]/ba - MP3 audio

⚙️ ADVANCED:
• bv*[vcodec^=av01]+ba[acodec^=opus] - AV1 + Opus
• worst - Lowest quality (testing)

💡 'bv*+ba' = Best video + best audio with automatic fallback
📦 FFmpeg installed - high quality merging available!"""

# UI Layout constants
PADDING_STANDARD = 8
PADDING_SMALL = 4
PADDING_LARGE = 15

# Message update interval (ms)
MESSAGE_UPDATE_INTERVAL = 100

# Process termination timeout (seconds)
PROCESS_TERMINATION_TIMEOUT = 3.0
