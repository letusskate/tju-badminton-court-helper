"""
WeChat H5 Browser Scraper

This module provides a Selenium-based web scraper that mimics WeChat's built-in browser.
The scraper can access WeChat service accounts (H5 pages) by setting the appropriate
User-Agent and browser configurations.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import Optional

import config


class WeChatBrowserScraper:
    """
    A Selenium-based web scraper that mimics WeChat's built-in browser.
    
    This class configures Chrome with a WeChat User-Agent to access H5 pages
    that are typically only accessible through WeChat's built-in browser.
    """
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        headless: bool = None,
        window_size: tuple = None,
        timeout: int = None
    ):
        """
        Initialize the WeChat browser scraper.
        
        Args:
            user_agent: Custom User-Agent string. If None, uses default WeChat User-Agent
            headless: Whether to run browser in headless mode. If None, uses config default
            window_size: Browser window size as (width, height). If None, uses config default
            timeout: Default wait timeout in seconds. If None, uses config default
        """
        self.user_agent = user_agent or config.DEFAULT_USER_AGENT
        self.headless = headless if headless is not None else config.HEADLESS
        self.window_size = window_size or (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.timeout = timeout or config.DEFAULT_TIMEOUT
        self.driver = None
        
    def _setup_chrome_options(self) -> Options:
        """
        Configure Chrome options to mimic WeChat browser.
        
        Returns:
            Configured Chrome options
        """
        chrome_options = Options()
        
        # Set WeChat User-Agent - this is the key to making the browser
        # appear as WeChat's built-in browser
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        
        # Run in headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set window size to mimic mobile device
        chrome_options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        
        # Additional options to make the browser more stable
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Mobile emulation settings
        mobile_emulation = {
            "deviceMetrics": {"width": self.window_size[0], "height": self.window_size[1], "pixelRatio": 3.0},
            "userAgent": self.user_agent
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        return chrome_options
    
    def start(self):
        """
        Start the browser with WeChat configuration.
        """
        if self.driver is not None:
            print("Browser is already running")
            return
        
        chrome_options = self._setup_chrome_options()
        
        # Use webdriver_manager to automatically manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Create the driver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to prevent detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"Browser started with User-Agent: {self.user_agent}")
    
    def open_url(self, url: str):
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        print(f"Navigating to: {url}")
        self.driver.get(url)
    
    def wait_for_element(self, by: By, value: str, timeout: Optional[int] = None):
        """
        Wait for an element to be present on the page.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.XPATH)
            value: The value to search for
            timeout: Maximum time to wait in seconds. If None, uses default timeout
            
        Returns:
            The WebElement once it's found
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_element_clickable(self, by: By, value: str, timeout: Optional[int] = None):
        """
        Wait for an element to be clickable.
        
        Args:
            by: The method to locate the element (e.g., By.ID, By.XPATH)
            value: The value to search for
            timeout: Maximum time to wait in seconds. If None, uses default timeout
            
        Returns:
            The WebElement once it's clickable
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def get_page_source(self) -> str:
        """
        Get the current page's HTML source.
        
        Returns:
            The page source as a string
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return self.driver.page_source
    
    def take_screenshot(self, filename: str):
        """
        Take a screenshot of the current page.
        
        Args:
            filename: The filename to save the screenshot to
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved to: {filename}")
    
    def execute_script(self, script: str, *args):
        """
        Execute JavaScript in the browser.
        
        Args:
            script: The JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            The return value from the script
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return self.driver.execute_script(script, *args)
    
    def get_cookies(self) -> list:
        """
        Get all cookies from the current session.
        
        Returns:
            List of cookie dictionaries
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return self.driver.get_cookies()
    
    def add_cookie(self, cookie_dict: dict):
        """
        Add a cookie to the current session.
        
        Args:
            cookie_dict: Dictionary containing cookie information
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.driver.add_cookie(cookie_dict)
    
    def close(self):
        """
        Close the browser.
        """
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
            print("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
