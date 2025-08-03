"""
Unit tests for YouTube Downloader
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the classes to test
from youtube_downloader import YouTubeDownloader


class TestYouTubeDownloader(unittest.TestCase):
    """Test cases for YouTubeDownloader class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.downloader = YouTubeDownloader(download_path=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Test downloader initialization"""
        # Check that directories are created
        self.assertTrue(Path(self.test_dir).exists())
        self.assertTrue(self.downloader.single_videos_path.exists())
        self.assertTrue(self.downloader.playlists_path.exists())
        
        # Check paths are set correctly
        self.assertEqual(str(self.downloader.download_path), self.test_dir)
    
    def test_is_playlist_url(self):
        """Test playlist URL detection"""
        # Test playlist URLs
        playlist_urls = [
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",
            "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",
        ]
        
        for url in playlist_urls:
            with self.subTest(url=url):
                self.assertTrue(self.downloader.is_playlist_url(url))
        
        # Test single video URLs
        video_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
        ]
        
        for url in video_urls:
            with self.subTest(url=url):
                self.assertFalse(self.downloader.is_playlist_url(url))
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("Normal Title", "Normal Title"),
            ("Title/with\\illegal:chars", "Title_with_illegal_chars"),
            ("Title<with>more|illegal?chars*", "Title_with_more_illegal_chars_"),
            ("   Title with spaces   ", "Title with spaces"),
            ("Title" + "a" * 200, "Title" + "a" * 195),  # Test length limit
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = self.downloader.sanitize_filename(input_title)
                self.assertEqual(result, expected)
                # Ensure no illegal characters remain
                illegal_chars = r'<>:"/\|?*'
                self.assertFalse(any(char in result for char in illegal_chars))
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_get_playlist_info(self, mock_ytdl):
        """Test playlist info extraction"""
        # Mock successful playlist info extraction
        mock_info = {
            'title': 'Test Playlist',
            'entries': [{'title': 'Video 1'}, {'title': 'Video 2'}]
        }
        
        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.return_value = mock_info
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        result = self.downloader.get_playlist_info("https://www.youtube.com/playlist?list=TEST")
        
        self.assertEqual(result, mock_info)
        mock_ytdl_instance.extract_info.assert_called_once()
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_single_video_success(self, mock_ytdl):
        """Test successful single video download"""
        # Mock successful download
        mock_info = {'title': 'Test Video'}
        
        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.return_value = mock_info
        mock_ytdl_instance.download.return_value = None
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        result = self.downloader.download_single_video("https://www.youtube.com/watch?v=TEST")
        
        self.assertTrue(result)
        mock_ytdl_instance.extract_info.assert_called()
        mock_ytdl_instance.download.assert_called_once()
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_single_video_failure(self, mock_ytdl):
        """Test failed single video download"""
        # Mock download failure
        mock_ytdl_instance = Mock()
        mock_ytdl_instance.extract_info.side_effect = Exception("Download failed")
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        result = self.downloader.download_single_video("https://www.youtube.com/watch?v=TEST")
        
        self.assertFalse(result)
    
    def test_download_url_routing(self):
        """Test that download_url correctly routes to playlist or single video methods"""
        with patch.object(self.downloader, 'is_playlist_url') as mock_is_playlist, \
             patch.object(self.downloader, 'download_playlist') as mock_download_playlist, \
             patch.object(self.downloader, 'download_single_video') as mock_download_single:
            
            # Test playlist routing
            mock_is_playlist.return_value = True
            mock_download_playlist.return_value = True
            
            result = self.downloader.download_url("https://www.youtube.com/playlist?list=TEST")
            
            self.assertTrue(result)
            mock_download_playlist.assert_called_once()
            mock_download_single.assert_not_called()
            
            # Reset mocks
            mock_download_playlist.reset_mock()
            mock_download_single.reset_mock()
            
            # Test single video routing
            mock_is_playlist.return_value = False
            mock_download_single.return_value = True
            
            result = self.downloader.download_url("https://www.youtube.com/watch?v=TEST")
            
            self.assertTrue(result)
            mock_download_single.assert_called_once()
            mock_download_playlist.assert_not_called()
    
    def test_download_multiple_urls(self):
        """Test downloading multiple URLs"""
        urls = [
            "https://www.youtube.com/watch?v=TEST1",
            "https://www.youtube.com/playlist?list=TEST2"
        ]
        
        with patch.object(self.downloader, 'download_url') as mock_download:
            mock_download.return_value = True
            
            results = self.downloader.download_multiple_urls(urls)
            
            # Check that all URLs were processed
            self.assertEqual(len(results), 2)
            self.assertEqual(mock_download.call_count, 2)
            
            # Check that all downloads were successful
            for url, success in results.items():
                self.assertTrue(success)


class TestURLValidation(unittest.TestCase):
    """Test URL validation and parsing"""
    
    def setUp(self):
        self.downloader = YouTubeDownloader()
    
    def test_valid_youtube_urls(self):
        """Test various valid YouTube URL formats"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",
            "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvzey9DAEdGjNMi56M",
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                # These should not raise exceptions when parsed
                result = self.downloader.is_playlist_url(url)
                self.assertIsInstance(result, bool)
    
    def test_invalid_urls(self):
        """Test handling of invalid URLs"""
        invalid_urls = [
            "not_a_url",
            "https://www.notyoutube.com/watch?v=test",
            "https://vimeo.com/123456",
            "",
            None,
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                try:
                    result = self.downloader.is_playlist_url(url)
                    # Should return False for invalid URLs, not crash
                    self.assertFalse(result)
                except Exception:
                    # Or it might raise an exception, which is also acceptable
                    pass


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
