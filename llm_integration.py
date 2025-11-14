"""
LLM Integration - Uses AI to understand natural language commands
Supports multiple providers: Ollama (local), OpenAI, Groq, Gemini
"""

import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMIntegration:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "ollama").lower()
        self.api_key = None
        self.setup_provider()
    
    def setup_provider(self):
        """Setup the AI provider based on configuration"""
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("⚠️  Warning: OPENAI_API_KEY not set. Using fallback parsing.")
        elif self.provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
        elif self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
        elif self.provider == "ollama":
            # Ollama doesn't need API key, runs locally
            pass
    
    def understand_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Use LLM to understand user command and extract action"""
        try:
            if self.provider == "ollama":
                return self._query_ollama(user_input)
            elif self.provider == "openai":
                return self._query_openai(user_input)
            elif self.provider == "groq":
                return self._query_groq(user_input)
            elif self.provider == "gemini":
                return self._query_gemini(user_input)
            else:
                return None
        except Exception as e:
            print(f"⚠️  LLM Error: {e}. Using fallback parsing.")
            return None
    
    def _query_ollama(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Query Ollama (local)"""
        try:
            import requests
            
            prompt = f"""Analyze this voice command and extract the action in JSON format:
Command: "{user_input}"

Return JSON with this structure:
{{
    "action": "open_website" | "open_app" | "click_first_link" | "click_link" | "go_to_search_bar" | "search" | "scroll_down" | "scroll_up" | "go_back" | "go_forward" | "refresh" | "unknown",
    "website": "youtube" | "instagram" | "google" | etc (if action is open_website),
    "app": "app_name" (if action is open_app),
    "search": "search query" (if user wants to search for something),
    "query": "search query" (alternative to search),
    "link_text": "text of link to click" (if action is click_link),
    "pixels": number (for scroll actions)
}}

Examples:
- "open YouTube and search for cats" -> {{"action": "open_website", "website": "youtube", "search": "cats"}}
- "open Instagram" -> {{"action": "open_website", "website": "instagram"}}
- "click the first link" -> {{"action": "click_first_link"}}
- "click the video link" -> {{"action": "click_link", "link_text": "video"}}
- "go to search bar and search for Python" -> {{"action": "go_to_search_bar"}} then {{"action": "search", "query": "Python"}}
- "search for cats" -> {{"action": "search", "query": "cats"}}
- "go to search bar" -> {{"action": "go_to_search_bar"}}
- "scroll down" -> {{"action": "scroll_down"}}
- "go back" -> {{"action": "go_back"}}
- "open Spotify" -> {{"action": "open_app", "app": "spotify"}}

Only return valid JSON, nothing else:"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Try to extract JSON from response
                try:
                    # Remove markdown code blocks if present
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    command_data = json.loads(response_text)
                    return command_data
                except json.JSONDecodeError:
                    # Try to find JSON object in text
                    import re
                    json_match = re.search(r'\{[^}]+\}', response_text)
                    if json_match:
                        return json.loads(json_match.group())
            
            return None
        except Exception as e:
            print(f"Ollama query error: {e}")
            return None
    
    def _query_openai(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Query OpenAI API"""
        try:
            import openai
            
            if not self.api_key:
                return None
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a command parser. Extract actions from voice commands and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f'Parse this command: "{user_input}"\n\nReturn JSON: {{"action": "open_website"|"open_app"|"unknown", "website": "...", "app": "...", "search": "..."}}'
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"OpenAI query error: {e}")
            return None
    
    def _query_groq(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Query Groq API"""
        try:
            from groq import Groq
            
            if not self.api_key:
                return None
            
            client = Groq(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract actions from voice commands. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f'Parse: "{user_input}"\n\nJSON: {{"action": "...", "website": "...", "app": "...", "search": "..."}}'
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Groq query error: {e}")
            return None
    
    def _query_gemini(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Query Google Gemini API"""
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                return None
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""Parse this voice command and return JSON:
"{user_input}"

Return JSON: {{"action": "open_website"|"open_app"|"unknown", "website": "...", "app": "...", "search": "..."}}"""
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON
            import re
            json_match = re.search(r'\{[^}]+\}', result_text)
            if json_match:
                return json.loads(json_match.group())
            
            return None
        except Exception as e:
            print(f"Gemini query error: {e}")
            return None

