# Smart Code Debugging Agent

An AI-powered tool that analyzes code and error messages to provide clear explanations and fixes.

## Features

- 📝 **Text Input**: Paste code or error messages directly
- 📸 **Image Upload**: Upload screenshots of code or errors
- 📄 **File Upload**: Upload code files or log files
- 🤖 **AI Analysis**: Uses Google's Gemini AI to detect and explain errors
- ✅ **Auto-Fix**: Generates corrected code automatically

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up Gemini API Key:**
   Create a `.env.local` file in the root directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Usage

1. **Option 1**: Paste your code or error message in the text area
2. **Option 2**: Upload a screenshot of your code/error
3. **Option 3**: Upload a code file or log file
4. Click the "Debug Code" button
5. View the results:
   - Error explanation
   - Reasoning
   - Fixed code

## Requirements

- Node.js 18+ 
- Google Gemini API key (Get it from https://makersuite.google.com/app/apikey)

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Google Gemini API** - AI processing (gemini-1.5-pro for multimodal support)

## Notes

- The tool works best with clear error messages or visible code
- Image analysis uses Gemini 1.5 Pro for vision capabilities
- Large files may take longer to process

