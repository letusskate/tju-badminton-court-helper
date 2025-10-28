"""
Tests for WeChat Browser Scraper

Basic tests to validate the scraper functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from wechat_scraper import WeChatBrowserScraper
import config


class TestWeChatBrowserScraper(unittest.TestCase):
    """Test cases for WeChatBrowserScraper class"""
    
    def test_initialization_default(self):
        """Test default initialization"""
        scraper = WeChatBrowserScraper()
        
        self.assertEqual(scraper.user_agent, config.DEFAULT_USER_AGENT)
        self.assertEqual(scraper.headless, config.HEADLESS)
        self.assertEqual(scraper.window_size, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.assertEqual(scraper.timeout, config.DEFAULT_TIMEOUT)
        self.assertIsNone(scraper.driver)
    
    def test_initialization_custom(self):
        """Test custom initialization"""
        custom_ua = "CustomUserAgent"
        custom_size = (400, 800)
        custom_timeout = 20
        
        scraper = WeChatBrowserScraper(
            user_agent=custom_ua,
            headless=True,
            window_size=custom_size,
            timeout=custom_timeout
        )
        
        self.assertEqual(scraper.user_agent, custom_ua)
        self.assertTrue(scraper.headless)
        self.assertEqual(scraper.window_size, custom_size)
        self.assertEqual(scraper.timeout, custom_timeout)
    
    def test_chrome_options_user_agent(self):
        """Test that Chrome options include correct User-Agent"""
        scraper = WeChatBrowserScraper()
        options = scraper._setup_chrome_options()
        
        # Check that user-agent argument is in the options
        user_agent_found = False
        for arg in options.arguments:
            if arg.startswith('user-agent=') and 'MicroMessenger' in arg:
                user_agent_found = True
                break
        
        self.assertTrue(user_agent_found, "User-Agent with MicroMessenger not found in Chrome options")
    
    def test_chrome_options_headless(self):
        """Test headless mode configuration"""
        scraper = WeChatBrowserScraper(headless=True)
        options = scraper._setup_chrome_options()
        
        self.assertIn('--headless', options.arguments)
    
    def test_chrome_options_window_size(self):
        """Test window size configuration"""
        window_size = (500, 900)
        scraper = WeChatBrowserScraper(window_size=window_size)
        options = scraper._setup_chrome_options()
        
        expected_arg = f'--window-size={window_size[0]},{window_size[1]}'
        self.assertIn(expected_arg, options.arguments)
    
    def test_chrome_options_mobile_emulation(self):
        """Test mobile emulation configuration"""
        scraper = WeChatBrowserScraper()
        options = scraper._setup_chrome_options()
        
        # Check mobile emulation is set
        mobile_emulation = options.experimental_options.get('mobileEmulation')
        self.assertIsNotNone(mobile_emulation)
        self.assertIn('deviceMetrics', mobile_emulation)
        self.assertIn('userAgent', mobile_emulation)
    
    def test_context_manager(self):
        """Test context manager protocol"""
        scraper = WeChatBrowserScraper()
        
        # Mock the start and close methods
        scraper.start = Mock()
        scraper.close = Mock()
        
        with scraper as s:
            self.assertEqual(s, scraper)
            scraper.start.assert_called_once()
        
        scraper.close.assert_called_once()
    
    def test_runtime_error_before_start(self):
        """Test that methods raise RuntimeError before start() is called"""
        scraper = WeChatBrowserScraper()
        
        with self.assertRaises(RuntimeError):
            scraper.open_url("https://example.com")
        
        with self.assertRaises(RuntimeError):
            scraper.get_page_source()
        
        with self.assertRaises(RuntimeError):
            scraper.take_screenshot("test.png")
    
    def test_user_agent_contains_micromessenger(self):
        """Test that default User-Agent contains MicroMessenger identifier"""
        scraper = WeChatBrowserScraper()
        self.assertIn('MicroMessenger', scraper.user_agent)
    
    def test_android_user_agent(self):
        """Test Android WeChat User-Agent"""
        self.assertIn('MicroMessenger', config.WECHAT_USER_AGENT_ANDROID)
        self.assertIn('Android', config.WECHAT_USER_AGENT_ANDROID)
    
    def test_ios_user_agent(self):
        """Test iOS WeChat User-Agent"""
        self.assertIn('MicroMessenger', config.WECHAT_USER_AGENT_IOS)
        self.assertIn('iPhone', config.WECHAT_USER_AGENT_IOS)


if __name__ == '__main__':
    unittest.main()
