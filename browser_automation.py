"""
Browser Automation - Controls web browser using Selenium
Handles clicking, searching, navigation, and interactions
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from typing import Optional, List

class BrowserAutomation:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.current_url: Optional[str] = None
        self._init_driver()
    
    def _init_driver(self):
        """Initialize the browser driver"""
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to initialize Chrome with webdriver-manager
            try:
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ Browser initialized successfully")
            except Exception as e:
                print(f"⚠️  Chrome with webdriver-manager failed. Trying direct Chrome...")
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    print("✅ Browser initialized successfully")
                except Exception as e2:
                    print(f"⚠️  Chrome driver not found. Trying Firefox...")
                    try:
                        from selenium.webdriver.firefox.options import Options as FirefoxOptions
                        from webdriver_manager.firefox import GeckoDriverManager
                        from selenium.webdriver.firefox.service import Service as FirefoxService
                        
                        firefox_options = FirefoxOptions()
                        service = FirefoxService(GeckoDriverManager().install())
                        self.driver = webdriver.Firefox(service=service, options=firefox_options)
                        print("✅ Firefox browser initialized")
                    except:
                        print(f"❌ Could not initialize browser: {e2}")
                        print("💡 Make sure Chrome or Firefox is installed")
                        self.driver = None
        except Exception as e:
            print(f"❌ Browser initialization error: {e}")
            print("💡 Install: pip install webdriver-manager")
            self.driver = None
    
    def is_available(self) -> bool:
        """Check if browser is available"""
        return self.driver is not None
    
    def open_website(self, url: str) -> bool:
        """Open a website"""
        if not self.driver:
            return False
        try:
            if not url.startswith("http"):
                url = f"https://{url}"
            self.driver.get(url)
            self.current_url = url
            time.sleep(2)  # Wait for page to load
            return True
        except Exception as e:
            print(f"Error opening website: {e}")
            return False
    
    def get_current_url(self) -> Optional[str]:
        """Get current page URL"""
        if not self.driver:
            return None
        try:
            return self.driver.current_url
        except:
            return None
    
    def click_first_link(self) -> bool:
        """Click the first clickable link on the page"""
        if not self.driver:
            return False
        try:
            # Wait for page to load
            time.sleep(1)
            
            # Try to find the first clickable link
            # Common selectors for links
            link_selectors = [
                "a[href]",  # Any anchor with href
                "a",  # Any anchor tag
                "[role='link']",  # Elements with link role
            ]
            
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # Filter visible and clickable links
                    for link in links:
                        if link.is_displayed() and link.is_enabled():
                            # Scroll into view
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(0.5)
                            link.click()
                            time.sleep(2)  # Wait for navigation
                            self.current_url = self.driver.current_url
                            return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"Error clicking first link: {e}")
            return False
    
    def click_link_by_text(self, text: str) -> bool:
        """Click a link containing specific text"""
        if not self.driver:
            return False
        try:
            # Find link by partial text match
            link = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, text))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            link.click()
            time.sleep(2)
            self.current_url = self.driver.current_url
            return True
        except:
            return False
    
    def search_in_search_bar(self, query: str, search_bar_selector: Optional[str] = None) -> bool:
        """Search in a search bar (works for YouTube, Google, etc.)"""
        if not self.driver:
            return False
        try:
            # Common search bar selectors for different sites
            current_url = self.driver.current_url.lower()
            
            # Determine search bar selector based on current site
            if search_bar_selector:
                selector = search_bar_selector
            elif "youtube.com" in current_url:
                selector = "input[name='search_query'], input[id='search'], input[placeholder*='Search']"
            elif "google.com" in current_url:
                selector = "input[name='q'], textarea[name='q']"
            elif "instagram.com" in current_url:
                selector = "input[placeholder*='Search'], input[type='text']"
            elif "facebook.com" in current_url:
                selector = "input[placeholder*='Search'], input[type='search']"
            else:
                # Generic search bar selectors
                selector = "input[type='search'], input[name*='search'], input[id*='search'], input[placeholder*='Search']"
            
            # Try to find and interact with search bar
            try:
                search_bar = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                search_bar.clear()
                search_bar.send_keys(query)
                time.sleep(0.5)
                search_bar.send_keys(Keys.RETURN)
                time.sleep(2)  # Wait for search results
                self.current_url = self.driver.current_url
                return True
            except TimeoutException:
                # Try alternative method - find any input field
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
                for inp in inputs:
                    if inp.is_displayed():
                        inp.clear()
                        inp.send_keys(query)
                        time.sleep(0.5)
                        inp.send_keys(Keys.RETURN)
                        time.sleep(2)
                        self.current_url = self.driver.current_url
                        return True
                return False
        except Exception as e:
            print(f"Error searching: {e}")
            return False
    
    def go_to_search_bar(self) -> bool:
        """Navigate to/focus on the search bar"""
        if not self.driver:
            return False
        try:
            current_url = self.driver.current_url.lower()
            
            # Site-specific search bar selectors
            if "youtube.com" in current_url:
                selector = "input[name='search_query']"
            elif "google.com" in current_url:
                selector = "input[name='q'], textarea[name='q']"
            else:
                selector = "input[type='search'], input[name*='search']"
            
            try:
                search_bar = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)
                search_bar.click()
                time.sleep(0.5)
                return True
            except:
                # Try clicking any visible search input
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
                for inp in inputs:
                    if inp.is_displayed():
                        inp.click()
                        return True
                return False
        except Exception as e:
            print(f"Error going to search bar: {e}")
            return False
    
    def click_element_by_text(self, text: str) -> bool:
        """Click any element containing specific text"""
        if not self.driver:
            return False
        try:
            # Try various methods to find element by text
            xpath = f"//*[contains(text(), '{text}')]"
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            time.sleep(1)
            return True
        except:
            return False
    
    def scroll_down(self, pixels: int = 500) -> bool:
        """Scroll down the page"""
        if not self.driver:
            return False
        try:
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            time.sleep(0.5)
            return True
        except:
            return False
    
    def scroll_up(self, pixels: int = 500) -> bool:
        """Scroll up the page"""
        if not self.driver:
            return False
        try:
            self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            time.sleep(0.5)
            return True
        except:
            return False
    
    def go_back(self) -> bool:
        """Go back in browser history"""
        if not self.driver:
            return False
        try:
            self.driver.back()
            time.sleep(1)
            self.current_url = self.driver.current_url
            return True
        except:
            return False
    
    def go_forward(self) -> bool:
        """Go forward in browser history"""
        if not self.driver:
            return False
        try:
            self.driver.forward()
            time.sleep(1)
            self.current_url = self.driver.current_url
            return True
        except:
            return False
    
    def refresh_page(self) -> bool:
        """Refresh the current page"""
        if not self.driver:
            return False
        try:
            self.driver.refresh()
            time.sleep(2)
            return True
        except:
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.current_url = None

