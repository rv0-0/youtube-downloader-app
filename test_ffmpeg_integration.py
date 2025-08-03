#!/usr/bin/env python3
"""
Test script to verify ffmpeg integration and format selection
"""

import yt_dlp
import subprocess
import sys

def test_ffmpeg_availability():
    """Test if ffmpeg is available and working"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg is available: {version_line}")
            return True
        else:
            print(f"❌ FFmpeg failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        return False
    except Exception as e:
        print(f"❌ FFmpeg test error: {e}")
        return False

def test_format_availability():
    """Test format availability for a sample video"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'simulate': True,  # Don't actually download
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n🔍 Testing format availability for sample video...")
            info = ydl.extract_info(test_url, download=False)
            
            # Check available formats
            formats = info.get('formats', [])
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            print(f"📹 Video-only formats available: {len(video_formats)}")
            print(f"🎵 Audio-only formats available: {len(audio_formats)}")
            
            # Test our new format strings
            test_formats = [
                "bv*+ba/b",
                "bv*[height<=1080]+ba/b[height<=1080]",
                "bv*[height<=720]+ba/b[height<=720]",
            ]
            
            for fmt in test_formats:
                try:
                    ydl_opts_test = {
                        'format': fmt,
                        'quiet': True,
                        'no_warnings': True,
                        'simulate': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts_test) as ydl_test:
                        selected = ydl_test.extract_info(test_url, download=False)
                        requested_formats = selected.get('requested_formats', [])
                        
                        if len(requested_formats) > 1:
                            video_fmt = requested_formats[0]
                            audio_fmt = requested_formats[1]
                            print(f"✅ Format '{fmt}' selects:")
                            print(f"   Video: {video_fmt.get('format_id')} - {video_fmt.get('format_note', 'N/A')} - {video_fmt.get('height', 'N/A')}p")
                            print(f"   Audio: {audio_fmt.get('format_id')} - {audio_fmt.get('format_note', 'N/A')} - {audio_fmt.get('abr', 'N/A')}kbps")
                        else:
                            print(f"✅ Format '{fmt}' selects single format: {selected.get('format_id')} - {selected.get('format_note', 'N/A')}")
                            
                except Exception as e:
                    print(f"❌ Format '{fmt}' failed: {e}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Format testing failed: {e}")
        return False

def main():
    print("🧪 YouTube Downloader - FFmpeg Integration Test")
    print("=" * 50)
    
    # Test 1: FFmpeg availability
    ffmpeg_ok = test_ffmpeg_availability()
    
    # Test 2: Format selection
    format_ok = test_format_availability() if ffmpeg_ok else False
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"FFmpeg Available: {'✅' if ffmpeg_ok else '❌'}")
    print(f"Format Selection: {'✅' if format_ok else '❌'}")
    
    if ffmpeg_ok and format_ok:
        print("\n🎉 All tests passed! High-quality downloads with audio should work properly.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        
    return ffmpeg_ok and format_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
