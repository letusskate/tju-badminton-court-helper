"""
Example usage of the WeChat Browser Scraper

This script demonstrates how to use the WeChatBrowserScraper class
to access WeChat H5 pages.
"""

from wechat_scraper import WeChatBrowserScraper
from selenium.webdriver.common.by import By
import time


def example_basic_usage():
    """
    Basic example: Opening a URL and taking a screenshot.
    """
    print("=== Basic Usage Example ===\n")
    
    # Create scraper instance
    scraper = WeChatBrowserScraper()
    
    try:
        # Start the browser
        scraper.start()
        
        # Navigate to a URL (replace with your WeChat H5 page URL)
        # Example: scraper.open_url("https://your-wechat-h5-page.com")
        scraper.open_url("https://www.baidu.com")
        
        # Wait for page to load
        time.sleep(3)
        
        # Take a screenshot
        scraper.take_screenshot("screenshot.png")
        
        # Get page source
        page_source = scraper.get_page_source()
        print(f"Page source length: {len(page_source)} characters")
        
    finally:
        # Always close the browser
        scraper.close()


def example_context_manager():
    """
    Example using context manager for automatic cleanup.
    """
    print("\n=== Context Manager Example ===\n")
    
    # Using context manager - browser will be automatically closed
    with WeChatBrowserScraper() as scraper:
        scraper.open_url("https://www.baidu.com")
        time.sleep(2)
        print("Page title:", scraper.driver.title)


def example_custom_config():
    """
    Example with custom configuration.
    """
    print("\n=== Custom Configuration Example ===\n")
    
    # Create scraper with custom settings
    custom_user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
        "MicroMessenger/8.0.20(0x18001428) NetType/WIFI Language/zh_CN"
    )
    
    scraper = WeChatBrowserScraper(
        user_agent=custom_user_agent,
        headless=False,  # Set to True to run without GUI
        window_size=(414, 896),  # iPhone XR size
        timeout=15
    )
    
    try:
        scraper.start()
        scraper.open_url("https://www.baidu.com")
        time.sleep(2)
        
        # Get cookies
        cookies = scraper.get_cookies()
        print(f"Number of cookies: {len(cookies)}")
        
    finally:
        scraper.close()


def example_element_interaction():
    """
    Example demonstrating how to wait for and interact with elements.
    """
    print("\n=== Element Interaction Example ===\n")
    
    with WeChatBrowserScraper() as scraper:
        scraper.open_url("https://www.baidu.com")
        
        # Wait for an element to be present
        try:
            # Example: Wait for search input (adjust selector for your needs)
            search_input = scraper.wait_for_element(By.ID, "kw", timeout=10)
            print("Search input found!")
            
            # Type into the input
            search_input.send_keys("WeChat H5")
            time.sleep(1)
            
            # Take screenshot of result
            scraper.take_screenshot("interaction_result.png")
            
        except Exception as e:
            print(f"Element not found: {e}")


def example_javascript_execution():
    """
    Example demonstrating JavaScript execution.
    """
    print("\n=== JavaScript Execution Example ===\n")
    
    with WeChatBrowserScraper() as scraper:
        scraper.open_url("https://www.baidu.com")
        time.sleep(2)
        
        # Execute JavaScript to get page information
        result = scraper.execute_script("return navigator.userAgent;")
        print(f"User-Agent from JavaScript: {result}")
        
        # Verify it contains 'MicroMessenger'
        if 'MicroMessenger' in result:
            print("✓ Successfully mimicking WeChat browser!")
        else:
            print("✗ WeChat User-Agent not detected")


if __name__ == "__main__":
    print("WeChat Browser Scraper - Example Usage\n")
    print("=" * 50)
    
    # Run examples
    # Uncomment the examples you want to run:
    
    # example_basic_usage()
    # example_context_manager()
    # example_custom_config()
    # example_element_interaction()
    example_javascript_execution()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
