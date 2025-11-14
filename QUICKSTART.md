# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Windows users:** If `pyaudio` fails, use:
```bash
pip install pipwin
pipwin install pyaudio
```

## Step 2: Set Up Ollama (100% FREE - Recommended!)

1. **Download Ollama:** https://ollama.ai (completely free!)
2. **Install and run it**
3. **Pull a model:**
   ```bash
   ollama pull llama3.2:3b
   ```

**💰 Cost:** $0.00 - Free forever, unlimited usage, no API keys needed!

## Step 3: Create Config File

```bash
cp config.example.env .env
```

Edit `.env` and make sure it has:
```
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```

## Step 4: Run!

**Terminal Mode:**
```bash
python voice_assistant.py
```

**GUI Mode:**
```bash
python voice_assistant.py --gui
```

## First Commands to Try

1. **"Open YouTube"** - Opens YouTube
2. **"Open YouTube and search for cats"** - Opens YouTube with search
3. **"Click the first link"** - Clicks the first link on the page
4. **"Go to search bar and search for Python"** - Uses search bar
5. **"Open Instagram"** - Opens Instagram
6. **"Scroll down"** - Scrolls the page
7. **"Exit"** or **"Thank you"** - Stops the assistant

**✨ The assistant runs continuously - it's always listening until you say quit!**

## Troubleshooting

### "No module named 'pyaudio'"
- Windows: `pip install pipwin && pipwin install pyaudio`
- Mac: `brew install portaudio && pip install pyaudio`
- Linux: `sudo apt-get install portaudio19-dev && pip install pyaudio`

### "Ollama connection error"
- Make sure Ollama is running: `ollama serve`
- Check if model exists: `ollama list`

### "Microphone not working"
- Check system microphone permissions
- Ensure microphone is not muted
- Try speaking louder or closer to mic

---

**That's it! You're ready to go! 🎉**

