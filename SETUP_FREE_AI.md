# Free AI Setup Guide

Since API credits are limited, here are **completely free alternatives** to use with this debugging tool:

## Option 1: Ollama (Recommended - 100% Free & Local) ⭐

**Best for:** Complete privacy, no internet needed, unlimited usage

### Setup:
1. **Install Ollama:**
   - Download from: https://ollama.ai
   - Install the application

2. **Pull a code model:**
   ```bash
   ollama pull llama3.2:3b
   ```
   Or for better code understanding:
   ```bash
   ollama pull codellama:7b
   ```

3. **Start Ollama:**
   - Ollama runs automatically after installation
   - Default URL: `http://localhost:11434`

4. **No API key needed!** Just use the app.

### Available Models:
- `llama3.2:3b` - Fast, lightweight (recommended)
- `codellama:7b` - Better for code
- `mistral:7b` - Good balance
- `llama3.2:1b` - Ultra-lightweight

---

## Option 2: Groq (Free API - Very Fast) 🚀

**Best for:** Fast responses, cloud-based, free tier

### Setup:
1. **Get API Key:**
   - Sign up at: https://console.groq.com
   - Create an API key (free tier available)

2. **Add to `.env.local`:**
   ```
   AI_PROVIDER=groq
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Restart your dev server**

**Free Tier:** Very generous limits, extremely fast responses

---

## Option 3: Hugging Face (Free Tier) 🤗

**Best for:** Access to many open-source models

### Setup:
1. **Get API Key:**
   - Sign up at: https://huggingface.co
   - Go to Settings > Access Tokens
   - Create a token

2. **Add to `.env.local`:**
   ```
   AI_PROVIDER=huggingface
   HUGGING_FACE_API_KEY=your_hf_token_here
   ```

---

## Quick Start (Ollama)

1. Install Ollama: https://ollama.ai
2. Run: `ollama pull llama3.2:3b`
3. That's it! The app will use Ollama automatically.

No API keys, no credits, completely free! 🎉

---

## Switching Providers

In `.env.local`, set:
```
AI_PROVIDER=ollama    # or groq, huggingface
```

Default is `ollama` if not specified.

