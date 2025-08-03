"""
Setup and installation script for YouTube Downloader
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True


def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    try:
        # Read requirements
        requirements_file = Path(__file__).parent / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        # Install packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["Downloads", "Downloads/Single Videos", "Downloads/Playlists"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")


def test_installation():
    """Test if installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Try importing the main modules
        import yt_dlp
        import colorama
        from youtube_downloader import YouTubeDownloader
        
        # Test creating downloader instance
        downloader = YouTubeDownloader("test_downloads")
        
        print("✅ Installation test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_usage_info():
    """Show usage information"""
    print("\n" + "="*60)
    print("🎬 YouTube Downloader - Installation Complete!")
    print("="*60)
    print()
    print("Usage options:")
    print()
    print("1. Command Line Interface:")
    print("   python youtube_downloader.py")
    print()
    print("2. Graphical User Interface:")
    print("   python gui.py")
    print()
    print("3. Batch Processing:")
    print("   python batch_download.py urls.txt")
    print("   python batch_download.py --create-sample urls.txt")
    print()
    print("4. Programmatic Usage:")
    print("   python examples.py")
    print()
    print("Examples:")
    print("   # Create sample URLs file")
    print("   python batch_download.py --create-sample my_urls.txt")
    print()
    print("   # Download from file")
    print("   python batch_download.py my_urls.txt -o MyVideos")
    print()
    print("   # Interactive download")
    print("   python youtube_downloader.py")
    print()
    print("Features:")
    print("- ✅ Single video downloads")
    print("- ✅ Playlist downloads with numbering")
    print("- ✅ Automatic URL type detection")
    print("- ✅ Organized folder structure")
    print("- ✅ Progress tracking")
    print("- ✅ Error handling")
    print()
    print("Note: Please respect YouTube's Terms of Service")
    print("="*60)


def main():
    """Main setup function"""
    print("🚀 YouTube Downloader Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install requirements")
        print("Try running manually: pip install -r requirements.txt")
        return False
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed: Installation test failed")
        return False
    
    # Show usage info
    show_usage_info()
    
    print("\n✅ Setup completed successfully!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
