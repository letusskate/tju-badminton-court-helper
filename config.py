"""
WeChat Browser Scraper Configuration

This module contains configuration settings for the WeChat H5 scraper.
"""

# WeChat User-Agent strings for different platforms

# Android WeChat User-Agent
# Contains 'MicroMessenger' which is the key identifier for WeChat browser
WECHAT_USER_AGENT_ANDROID = (
    "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile "
    "Safari/537.36 MicroMessenger/8.0.30.1810(0x28001030) Process/tools"
)

# iOS WeChat User-Agent
# Alternative User-Agent for iOS devices
WECHAT_USER_AGENT_IOS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.20(0x18001428) NetType/WIFI Language/zh_CN"
)

# Default User-Agent to use (Android)
DEFAULT_USER_AGENT = WECHAT_USER_AGENT_ANDROID

# Browser window size
WINDOW_WIDTH = 375  # Common mobile width
WINDOW_HEIGHT = 812  # Common mobile height

# Wait timeout (in seconds)
DEFAULT_TIMEOUT = 10

# Whether to run browser in headless mode
HEADLESS = False
