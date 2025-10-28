"""
Integration test to verify the scraper can start a browser
and verify the User-Agent is set correctly.
"""

from wechat_scraper import WeChatBrowserScraper
import sys


def test_scraper_integration():
    """
    Integration test to verify:
    1. Browser can start
    2. User-Agent is set correctly with MicroMessenger
    3. Browser can navigate to a URL
    4. Browser can execute JavaScript
    """
    print("Starting integration test...")
    
    try:
        # Create scraper in headless mode for CI/CD compatibility
        scraper = WeChatBrowserScraper(headless=True, timeout=20)
        
        # Start browser
        print("✓ Starting browser...")
        scraper.start()
        
        # Navigate to a simple page
        print("✓ Navigating to test page...")
        scraper.open_url("https://httpbin.org/headers")
        
        # Wait a moment for page to load
        import time
        time.sleep(3)
        
        # Execute JavaScript to verify User-Agent
        print("✓ Verifying User-Agent...")
        user_agent = scraper.execute_script("return navigator.userAgent;")
        
        # Check if MicroMessenger is in the User-Agent
        if 'MicroMessenger' in user_agent:
            print(f"✓ SUCCESS: User-Agent contains 'MicroMessenger'")
            print(f"  User-Agent: {user_agent}")
            success = True
        else:
            print(f"✗ FAILED: User-Agent does not contain 'MicroMessenger'")
            print(f"  User-Agent: {user_agent}")
            success = False
        
        # Get page source to verify we got a response
        page_source = scraper.get_page_source()
        if len(page_source) > 0:
            print(f"✓ Page loaded successfully (source length: {len(page_source)} chars)")
        else:
            print("✗ Failed to load page")
            success = False
        
        # Take a screenshot
        screenshot_path = "/tmp/integration_test_screenshot.png"
        scraper.take_screenshot(screenshot_path)
        print(f"✓ Screenshot saved to {screenshot_path}")
        
        # Close browser
        scraper.close()
        print("✓ Browser closed")
        
        return success
        
    except Exception as e:
        print(f"✗ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_scraper_integration()
    
    if success:
        print("\n" + "=" * 50)
        print("Integration test PASSED")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("Integration test FAILED")
        print("=" * 50)
        sys.exit(1)
