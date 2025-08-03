"""
GUI version of the YouTube Downloader using tkinter
Enhanced with quality selection and individual video progress tracking

This is the modular version that uses separate components for better code organization.
The original monolithic version has been backed up as gui_original.py

Modular Structure:
- gui/constants.py: Configuration constants and settings
- gui/ui_components.py: UI widget creation and setup
- gui/progress_tracker.py: Progress tracking functionality
- gui/download_manager.py: Download processes and threading
- gui/main_window.py: Main window coordination
"""

# Import the modular main window
from gui.main_window import YouTubeDownloaderGUI, main

# Re-export for backward compatibility
__all__ = ['YouTubeDownloaderGUI', 'main']

if __name__ == "__main__":
    main()
