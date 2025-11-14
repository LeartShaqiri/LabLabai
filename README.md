# Comet Voice Assistant

A local voice-activated AI assistant that runs on your computer. Control your computer with voice commands - open websites, launch applications, and more!

## Features

- 🎤 **Voice Recognition** - Speak commands naturally
- 🔊 **Text-to-Speech** - Assistant responds with voice
- 🔄 **Continuous Listening** - Always listening until you say quit/stop
- 🌐 **Website Control** - Open YouTube, Instagram, Google, and more
- 🖱️ **Browser Automation** - Click links, use search bars, scroll pages
- 📱 **App Launcher** - Open applications on your system
- 🔍 **Smart Search** - "Open YouTube and search for cats" - it just works!
- 🖥️ **Terminal & GUI Modes** - Run in terminal or with a GUI
- 🤖 **AI-Powered** - Uses LLM to understand natural language commands

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users:** If `pyaudio` installation fails, install it separately:
```bash
pip install pipwin
pipwin install pyaudio
```

Or download the wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 2. Set Up AI Provider (Choose One)

#### Option A: Ollama (Recommended - Free & Local) ⭐

1. **Install Ollama:**
   - Download from: https://ollama.ai
   - Install and run it

2. **Pull a model:**
   ```bash
   ollama pull llama3.2:3b
   ```

3. **Create `.env` file:**
   ```bash
   cp config.example.env .env
   ```
   Edit `.env` and set:
   ```
   AI_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2:3b
   ```

**That's it!** No API keys needed. Works completely offline.

#### Option B: OpenAI

1. Get API key from: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_key_here
   ```

#### Option C: Groq (Free & Fast)

1. Get API key from: https://console.groq.com
2. Add to `.env`:
   ```
   AI_PROVIDER=groq
   GROQ_API_KEY=your_key_here
   ```

#### Option D: Gemini (Free Tier Available)

1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to `.env`:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   ```

### 3. Run the Assistant

**Terminal Mode:**
```bash
python voice_assistant.py
```

**GUI Mode:**
```bash
python voice_assistant.py --gui
```

## Usage Examples

### Voice Commands

**Website Control:**
- **"Open YouTube"** - Opens YouTube in browser
- **"Open YouTube and search for cats"** - Opens YouTube and searches
- **"Open Instagram"** - Opens Instagram in browser
- **"Open Google and search for Python tutorials"** - Opens Google with search

**Browser Interactions (NEW!):**
- **"Click the first link"** - Clicks the first clickable link on the page
- **"Go to search bar"** - Focuses on the search bar
- **"Go to search bar and search for Python"** - Goes to search bar and searches
- **"Search for cats"** - Searches in the current page's search bar
- **"Scroll down"** - Scrolls down the page
- **"Scroll up"** - Scrolls up the page
- **"Go back"** - Goes back in browser history
- **"Go forward"** - Goes forward in browser history
- **"Refresh"** - Refreshes the current page

**App Control:**
- **"Open Spotify"** - Launches Spotify app
- **"Open Discord"** - Opens Discord
- **"Open Notepad"** - Opens Notepad (Windows)

**Stop Assistant:**
- **"Exit"**, **"Quit"**, **"Stop"**, **"Thank you"**, **"Goodbye"** - Stops the assistant

### Supported Websites

YouTube, Instagram, Facebook, Twitter/X, LinkedIn, GitHub, Reddit, Google, Gmail, Netflix, Spotify, Discord, Twitch, and more!

### Supported Apps (Windows)

Notepad, Calculator, Paint, Chrome, Firefox, Edge, Spotify, Discord, Steam, VS Code, and more!

## How It Works

1. **Voice Input** - Microphone captures your speech
2. **Speech Recognition** - Converts speech to text (Google Speech Recognition)
3. **AI Understanding** - LLM analyzes the command and extracts intent
4. **Action Execution** - Assistant performs the requested action
5. **Voice Response** - Assistant confirms with text-to-speech

## Requirements

- Python 3.8+
- Microphone
- Chrome or Firefox browser (for browser automation features)
- Internet connection (for speech recognition, unless using offline mode)
- AI Provider (Ollama recommended - **100% free & unlimited usage**)

## 💰 Cost & Usage

**🆓 FREE Options Available!**

- **Ollama (Recommended):** 100% free, unlimited usage, no API keys, works offline
- **Groq:** Free tier with generous limits
- **Gemini:** Free tier available
- **OpenAI:** Pay-per-use (not free)

See [PRICING_GUIDE.md](PRICING_GUIDE.md) for detailed pricing information.

**Quick answer: Yes, you can use this completely free with unlimited usage using Ollama!**

## Troubleshooting

### Microphone Not Working

- Check microphone permissions in system settings
- Ensure microphone is not muted
- Try a different microphone

### Speech Recognition Issues

- Ensure you have internet connection (Google Speech Recognition requires internet)
- Speak clearly and wait for the "Listening..." prompt
- Reduce background noise

### Ollama Connection Error

- Make sure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`
- Verify Ollama is accessible at `http://localhost:11434`

### App Won't Open

- Check if the app is installed
- Try using the full app name
- On Windows, some apps need to be in PATH

### Browser Automation Not Working

- Make sure Chrome or Firefox is installed
- Install webdriver-manager: `pip install webdriver-manager`
- The browser driver will be downloaded automatically on first run
- If issues persist, try updating Chrome/Firefox to the latest version

## Advanced Configuration

### Using Offline Speech Recognition

Install PocketSphinx for offline recognition:
```bash
pip install pocketsphinx
```

The assistant will automatically fall back to offline recognition if internet is unavailable.

### Custom Commands

Edit `command_handler.py` to add custom commands or modify existing ones.

### Change TTS Voice

Edit `voice_assistant.py` and modify the TTS engine properties:
```python
self.tts_engine.setProperty('rate', 150)  # Speed
self.tts_engine.setProperty('volume', 0.9)  # Volume
```

## Project Structure

```
.
├── voice_assistant.py      # Main assistant script
├── command_handler.py      # Handles command execution
├── llm_integration.py      # AI/LLM integration
├── requirements.txt        # Python dependencies
├── config.example.env      # Configuration template
└── README.md              # This file
```

## License

Free to use and modify!

## Contributing

Feel free to submit issues, fork the repository, and create pull requests!

---

**Enjoy your voice-controlled assistant! 🎙️✨**
