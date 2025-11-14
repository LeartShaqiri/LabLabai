"""
Command Handler - Executes various commands like opening websites and apps
"""

import webbrowser
import subprocess
import platform
import os
from typing import Optional
from browser_automation import BrowserAutomation

class CommandHandler:
    def __init__(self):
        self.system = platform.system()
        self.browser_automation = BrowserAutomation()
        self.use_browser_automation = self.browser_automation.is_available()
        self.website_urls = {
            "youtube": "https://www.youtube.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "x": "https://www.x.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://www.github.com",
            "reddit": "https://www.reddit.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "discord": "https://discord.com",
            "twitch": "https://www.twitch.tv"
        }
    
    def open_website(self, website: str, search_query: Optional[str] = None) -> bool:
        """Open a website in the browser (using automation if available)"""
        try:
            website_lower = website.lower()
            
            # Get base URL
            base_url = self.website_urls.get(website_lower)
            if not base_url:
                base_url = f"https://www.{website_lower}.com"
            
            # Use browser automation if available (for better control)
            if self.use_browser_automation:
                if self.browser_automation.open_website(base_url):
                    if search_query:
                        # Wait a bit for page to load, then search
                        import time
                        time.sleep(2)
                        return self.browser_automation.search_in_search_bar(search_query)
                    return True
                return False
            else:
                # Fallback to simple webbrowser
                if search_query:
                    if website_lower == "youtube":
                        url = f"https://www.youtube.com/results?search_query={self._url_encode(search_query)}"
                    elif website_lower == "google":
                        url = f"https://www.google.com/search?q={self._url_encode(search_query)}"
                    else:
                        url = f"{base_url}/search?q={self._url_encode(search_query)}"
                else:
                    url = base_url
                
                webbrowser.open(url)
                return True
        except Exception as e:
            print(f"Error opening website {website}: {e}")
            return False
    
    def click_first_link(self) -> bool:
        """Click the first link on the current page"""
        if self.use_browser_automation:
            return self.browser_automation.click_first_link()
        else:
            print("⚠️  Browser automation not available. Install Selenium for this feature.")
            return False
    
    def click_link(self, link_text: str) -> bool:
        """Click a link by text"""
        if self.use_browser_automation:
            return self.browser_automation.click_link_by_text(link_text)
        else:
            print("⚠️  Browser automation not available.")
            return False
    
    def go_to_search_bar(self) -> bool:
        """Navigate to the search bar"""
        if self.use_browser_automation:
            return self.browser_automation.go_to_search_bar()
        else:
            print("⚠️  Browser automation not available.")
            return False
    
    def search_in_current_page(self, query: str) -> bool:
        """Search in the current page's search bar"""
        if self.use_browser_automation:
            return self.browser_automation.search_in_search_bar(query)
        else:
            print("⚠️  Browser automation not available.")
            return False
    
    def scroll_down(self, pixels: int = 500) -> bool:
        """Scroll down the page"""
        if self.use_browser_automation:
            return self.browser_automation.scroll_down(pixels)
        return False
    
    def scroll_up(self, pixels: int = 500) -> bool:
        """Scroll up the page"""
        if self.use_browser_automation:
            return self.browser_automation.scroll_up(pixels)
        return False
    
    def go_back(self) -> bool:
        """Go back in browser"""
        if self.use_browser_automation:
            return self.browser_automation.go_back()
        return False
    
    def go_forward(self) -> bool:
        """Go forward in browser"""
        if self.use_browser_automation:
            return self.browser_automation.go_forward()
        return False
    
    def refresh_page(self) -> bool:
        """Refresh current page"""
        if self.use_browser_automation:
            return self.browser_automation.refresh_page()
        return False
    
    def close_browser(self):
        """Close the browser"""
        if self.use_browser_automation:
            self.browser_automation.close()
    
    def open_app(self, app_name: str) -> bool:
        """Open an application on the system"""
        try:
            app_name_lower = app_name.lower()
            
            # Windows applications
            if self.system == "Windows":
                return self._open_windows_app(app_name_lower)
            # macOS applications
            elif self.system == "Darwin":
                return self._open_macos_app(app_name_lower)
            # Linux applications
            else:
                return self._open_linux_app(app_name_lower)
        except Exception as e:
            print(f"Error opening app {app_name}: {e}")
            return False
    
    def _open_windows_app(self, app_name: str) -> bool:
        """Open Windows application"""
        # Common Windows apps
        windows_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "steam": "steam.exe",
            "vscode": "code.exe",
            "code": "code.exe"
        }
        
        app_executable = windows_apps.get(app_name)
        if app_executable:
            try:
                subprocess.Popen([app_executable], shell=True)
                return True
            except:
                pass
        
        # Try to find app in common locations
        common_paths = [
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expanduser("~\\Desktop")
        ]
        
        # Try opening with start command
        try:
            subprocess.Popen(f'start {app_name}', shell=True)
            return True
        except:
            pass
        
        return False
    
    def _open_macos_app(self, app_name: str) -> bool:
        """Open macOS application"""
        # Common macOS apps
        macos_apps = {
            "safari": "Safari",
            "chrome": "Google Chrome",
            "firefox": "Firefox",
            "spotify": "Spotify",
            "discord": "Discord",
            "notes": "Notes",
            "calculator": "Calculator",
            "mail": "Mail",
            "messages": "Messages"
        }
        
        app_name_mac = macos_apps.get(app_name, app_name.capitalize())
        
        try:
            subprocess.Popen(["open", "-a", app_name_mac])
            return True
        except:
            return False
    
    def _open_linux_app(self, app_name: str) -> bool:
        """Open Linux application"""
        try:
            # Try common desktop environments
            subprocess.Popen([app_name], shell=True)
            return True
        except:
            # Try with xdg-open
            try:
                subprocess.Popen(["xdg-open", app_name])
                return True
            except:
                return False
    
    def _url_encode(self, text: str) -> str:
        """Simple URL encoding"""
        import urllib.parse
        return urllib.parse.quote_plus(text)
    
    def execute_system_command(self, command: str) -> bool:
        """Execute a system command"""
        try:
            if self.system == "Windows":
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen(command, shell=True)
            return True
        except Exception as e:
            print(f"Error executing command: {e}")
            return False

