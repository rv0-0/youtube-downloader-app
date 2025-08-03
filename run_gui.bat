@echo off
echo Starting YouTube Downloader GUI...
cd /d "%~dp0"
python gui.py
if errorlevel 1 (
    echo.
    echo Error: Failed to start the GUI. Make sure Python and dependencies are installed.
    echo Run: pip install -r requirements.txt
    pause
)
