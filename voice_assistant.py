#!/usr/bin/env python3
"""
Comet Voice Assistant - A local voice-activated AI assistant
Can run in terminal or GUI mode
"""

import speech_recognition as sr
import pyttsx3
import json
import os
import sys
from typing import Optional, Dict, Any
from command_handler import CommandHandler
from llm_integration import LLMIntegration
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self, use_gui: bool = False):
        """Initialize the voice assistant"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_handler = CommandHandler()
        self.llm = LLMIntegration()
        self.use_gui = use_gui
        self.is_listening = False
        self.is_running = True
        
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
        except Exception as e:
            print(f"Warning: Could not initialize TTS engine: {e}")
            self.tts_engine = None
        
        # Calibrate microphone for ambient noise
        print("Calibrating microphone for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone calibrated!")
    
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"🤖 Assistant: {text}")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            try:
                # Try Google Speech Recognition first (free, requires internet)
                text = self.recognizer.recognize_google(audio)
                print(f"📝 You said: {text}")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Error with speech recognition service: {e}")
                # Fallback to offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"📝 You said (offline): {text}")
                    return text
                except:
                    return None
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected")
            return None
        except Exception as e:
            print(f"❌ Error listening: {e}")
            return None
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process user command using LLM to understand intent"""
        print(f"🧠 Understanding command: {user_input}")
        
        # Use LLM to understand the command and extract action
        llm_response = self.llm.understand_command(user_input)
        
        if llm_response:
            return llm_response
        else:
            # Fallback to simple keyword matching
            return self._simple_command_parse(user_input)
    
    def _simple_command_parse(self, text: str) -> Dict[str, Any]:
        """Simple fallback command parser using keywords"""
        text_lower = text.lower()
        
        # Click first link
        if any(phrase in text_lower for phrase in ["click first link", "click the first link", "first link"]):
            return {"action": "click_first_link"}
        
        # Click link by text
        if "click" in text_lower and "link" in text_lower:
            # Try to extract link text
            words = text_lower.split()
            if "click" in words:
                click_idx = words.index("click")
                # Get words after "click"
                link_text = " ".join(words[click_idx + 1:])
                return {"action": "click_link", "link_text": link_text}
        
        # Go to search bar
        if any(phrase in text_lower for phrase in ["go to search bar", "search bar", "focus search"]):
            return {"action": "go_to_search_bar"}
        
        # Search in current page
        if any(phrase in text_lower for phrase in ["search for", "search in", "search youtube", "search google"]):
            query = self._extract_search_query(text, "search")
            if query:
                return {"action": "search", "query": query}
        
        # Scroll commands
        if "scroll down" in text_lower:
            return {"action": "scroll_down"}
        if "scroll up" in text_lower:
            return {"action": "scroll_up"}
        
        # Navigation
        if "go back" in text_lower or "back" in text_lower:
            return {"action": "go_back"}
        if "go forward" in text_lower or "forward" in text_lower:
            return {"action": "go_forward"}
        if "refresh" in text_lower:
            return {"action": "refresh"}
        
        # Open website commands
        if "youtube" in text_lower or "open youtube" in text_lower:
            search_query = self._extract_search_query(text, "youtube")
            return {
                "action": "open_website",
                "website": "youtube",
                "search": search_query
            }
        elif "instagram" in text_lower or "open instagram" in text_lower:
            return {
                "action": "open_website",
                "website": "instagram"
            }
        elif "google" in text_lower or ("open" in text_lower and "google" in text_lower):
            search_query = self._extract_search_query(text, "google")
            return {
                "action": "open_website",
                "website": "google",
                "search": search_query
            }
        elif "open" in text_lower:
            # Try to extract app/website name
            words = text_lower.split()
            if "open" in words:
                idx = words.index("open")
                if idx + 1 < len(words):
                    app_name = words[idx + 1]
                    return {
                        "action": "open_app",
                        "app": app_name
                    }
        
        return {
            "action": "unknown",
            "message": "I didn't understand that command"
        }
    
    def _extract_search_query(self, text: str, keyword: str) -> Optional[str]:
        """Extract search query from command"""
        text_lower = text.lower()
        keyword_idx = text_lower.find(keyword)
        
        if keyword_idx != -1:
            # Look for "search for" or "search" after the keyword
            search_patterns = ["search for", "search", "find"]
            for pattern in search_patterns:
                pattern_idx = text_lower.find(pattern, keyword_idx)
                if pattern_idx != -1:
                    query_start = pattern_idx + len(pattern)
                    query = text[query_start:].strip()
                    if query:
                        return query
        
        return None
    
    def execute_command(self, command: Dict[str, Any]) -> bool:
        """Execute the parsed command"""
        action = command.get("action")
        
        if action == "open_website":
            website = command.get("website")
            search = command.get("search")
            result = self.command_handler.open_website(website, search)
            if result:
                self.speak(f"Opening {website}" + (f" and searching for {search}" if search else ""))
            else:
                self.speak(f"Sorry, I couldn't open {website}")
            return result
        
        elif action == "open_app":
            app = command.get("app")
            result = self.command_handler.open_app(app)
            if result:
                self.speak(f"Opening {app}")
            else:
                self.speak(f"Sorry, I couldn't open {app}")
            return result
        
        elif action == "click_first_link":
            result = self.command_handler.click_first_link()
            if result:
                self.speak("Clicked the first link")
            else:
                self.speak("Sorry, I couldn't find a link to click")
            return result
        
        elif action == "click_link":
            link_text = command.get("link_text")
            result = self.command_handler.click_link(link_text)
            if result:
                self.speak(f"Clicked the link")
            else:
                self.speak("Sorry, I couldn't find that link")
            return result
        
        elif action == "go_to_search_bar":
            result = self.command_handler.go_to_search_bar()
            if result:
                self.speak("Went to the search bar")
            else:
                self.speak("Sorry, I couldn't find the search bar")
            return result
        
        elif action == "search":
            query = command.get("query") or command.get("search")
            result = self.command_handler.search_in_current_page(query)
            if result:
                self.speak(f"Searching for {query}")
            else:
                self.speak("Sorry, I couldn't perform the search")
            return result
        
        elif action == "scroll_down":
            pixels = command.get("pixels", 500)
            result = self.command_handler.scroll_down(pixels)
            if result:
                self.speak("Scrolled down")
            return result
        
        elif action == "scroll_up":
            pixels = command.get("pixels", 500)
            result = self.command_handler.scroll_up(pixels)
            if result:
                self.speak("Scrolled up")
            return result
        
        elif action == "go_back":
            result = self.command_handler.go_back()
            if result:
                self.speak("Going back")
            return result
        
        elif action == "go_forward":
            result = self.command_handler.go_forward()
            if result:
                self.speak("Going forward")
            return result
        
        elif action == "refresh":
            result = self.command_handler.refresh_page()
            if result:
                self.speak("Refreshing page")
            return result
        
        elif action == "unknown":
            message = command.get("message", "I didn't understand that")
            self.speak(message)
            return False
        
        else:
            self.speak("I'm not sure how to do that yet")
            return False
    
    def run_terminal_mode(self):
        """Run assistant in terminal mode - continuous listening"""
        print("\n" + "="*60)
        print("🎙️  Comet Voice Assistant - Terminal Mode")
        print("="*60)
        print("\n✨ CONTINUOUS LISTENING MODE - Always listening!")
        print("\nCommands:")
        print("  - Say 'open YouTube and search for [query]'")
        print("  - Say 'click the first link'")
        print("  - Say 'go to search bar and search for [query]'")
        print("  - Say 'open Instagram'")
        print("  - Say 'open [app name]'")
        print("  - Say 'exit', 'quit', 'stop', 'goodbye', or 'thank you' to stop")
        print("\n" + "-"*60 + "\n")
        
        self.speak("Voice assistant ready. I'm always listening. How can I help you?")
        
        while self.is_running:
            try:
                user_input = self.listen()
                
                if user_input:
                    user_lower = user_input.lower()
                    
                    # Check for exit commands (expanded list)
                    exit_keywords = [
                        "exit", "quit", "stop", "goodbye", "bye", 
                        "thank you", "thanks", "have a good day",
                        "see you", "later", "that's all"
                    ]
                    if any(keyword in user_lower for keyword in exit_keywords):
                        self.speak("Goodbye! Have a great day!")
                        # Close browser if open
                        self.command_handler.close_browser()
                        break
                    
                    # Process and execute command
                    command = self.process_command(user_input)
                    self.execute_command(command)
                    
                    # Small delay before listening again
                    time.sleep(0.5)
                else:
                    # If no input detected, continue listening
                    time.sleep(0.3)
                
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                self.speak("Goodbye!")
                self.command_handler.close_browser()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)
    
    def run_gui_mode(self):
        """Run assistant in GUI mode"""
        try:
            import tkinter as tk
            from tkinter import scrolledtext, ttk
        except ImportError:
            print("❌ Tkinter not available. Falling back to terminal mode.")
            self.run_terminal_mode()
            return
        
        root = tk.Tk()
        root.title("Comet Voice Assistant")
        root.geometry("600x500")
        root.configure(bg="#1a1a2e")
        
        # Create GUI elements
        title_label = tk.Label(
            root, 
            text="🎙️ Comet Voice Assistant", 
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#00d4ff"
        )
        title_label.pack(pady=20)
        
        status_label = tk.Label(
            root,
            text="Status: Ready",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#00ff88"
        )
        status_label.pack(pady=5)
        
        # Text display area
        text_area = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=70,
            height=20,
            bg="#16213e",
            fg="#e0e7ff",
            font=("Consolas", 10),
            insertbackground="#00d4ff"
        )
        text_area.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, "Voice Assistant Ready!\n")
        text_area.insert(tk.END, "Click 'Start Listening' to begin.\n\n")
        
        def log_message(message: str):
            text_area.insert(tk.END, f"{message}\n")
            text_area.see(tk.END)
        
        def listen_and_process():
            if self.is_listening:
                return
            
            self.is_listening = True
            status_label.config(text="Status: Listening...", fg="#ffaa00")
            log_message("🎤 Listening...")
            
            def process():
                user_input = self.listen()
                if user_input:
                    log_message(f"📝 You said: {user_input}")
                    
                    if any(word in user_input.lower() for word in ["exit", "quit", "stop"]):
                        log_message("👋 Shutting down...")
                        root.after(1000, root.destroy)
                        return
                    
                    command = self.process_command(user_input)
                    log_message(f"🧠 Action: {command.get('action', 'unknown')}")
                    self.execute_command(command)
                else:
                    log_message("❌ Could not understand audio")
                
                status_label.config(text="Status: Ready", fg="#00ff88")
                self.is_listening = False
            
            threading.Thread(target=process, daemon=True).start()
        
        # Buttons
        button_frame = tk.Frame(root, bg="#1a1a2e")
        button_frame.pack(pady=10)
        
        listen_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            command=listen_and_process,
            bg="#00d4ff",
            fg="#1a1a2e",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        listen_button.pack(side=tk.LEFT, padx=10)
        
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=lambda: root.destroy(),
            bg="#ff4444",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Override speak to also log to GUI
        original_speak = self.speak
        def gui_speak(text: str):
            log_message(f"🤖 Assistant: {text}")
            original_speak(text)
        self.speak = gui_speak
        
        root.mainloop()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comet Voice Assistant")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run in GUI mode (default: terminal mode)"
    )
    args = parser.parse_args()
    
    assistant = VoiceAssistant(use_gui=args.gui)
    
    if args.gui:
        assistant.run_gui_mode()
    else:
        assistant.run_terminal_mode()

if __name__ == "__main__":
    main()

