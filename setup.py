#!/usr/bin/env python3
"""
Setup script for Comet Voice Assistant
Helps with initial setup and dependency installation
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("\n💡 Try installing manually:")
        print("   pip install -r requirements.txt")
        return False

def setup_ollama():
    """Guide user through Ollama setup"""
    print("\n🤖 Ollama Setup (Recommended)")
    print("=" * 50)
    print("1. Download Ollama from: https://ollama.ai")
    print("2. Install and run Ollama")
    print("3. Pull a model:")
    print("   ollama pull llama3.2:3b")
    print("\n💡 Ollama is free, local, and works offline!")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return
    
    if os.path.exists("config.example.env"):
        print("\n📝 Creating .env file from template...")
        try:
            with open("config.example.env", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("✅ .env file created!")
            print("💡 Edit .env to configure your AI provider")
        except Exception as e:
            print(f"❌ Error creating .env: {e}")
    else:
        print("⚠️  config.example.env not found")

def check_microphone():
    """Check if microphone is available"""
    print("\n🎤 Checking microphone...")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            print("✅ Microphone detected!")
            return True
    except Exception as e:
        print(f"⚠️  Microphone check failed: {e}")
        print("   Make sure your microphone is connected and working")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 Comet Voice Assistant - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup incomplete. Please install dependencies manually.")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check microphone
    check_microphone()
    
    # Setup guide
    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("=" * 60)
    print("\n1. Configure AI Provider:")
    setup_ollama()
    print("\n2. Edit .env file to set your AI provider")
    print("\n3. Run the assistant:")
    print("   python voice_assistant.py          # Terminal mode")
    print("   python voice_assistant.py --gui    # GUI mode")
    print("\n" + "=" * 60)
    print("✅ Setup complete! You're ready to go!")
    print("=" * 60)

if __name__ == "__main__":
    main()

