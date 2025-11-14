import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

// Configure route for file uploads
export const runtime = 'nodejs'
export const maxDuration = 60

// Determine which AI provider to use
function getAIProvider() {
  const provider = process.env.AI_PROVIDER || 'gemini'
  
  return {
    provider,
    geminiApiKey: process.env.GEMINI_API_KEY,
    ollamaUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
    groqApiKey: process.env.GROQ_API_KEY,
  }
}

// Initialize Gemini client
function getGeminiClient() {
  const apiKey = process.env.GEMINI_API_KEY
  
  if (!apiKey) {
    throw new Error('GEMINI_API_KEY is not configured in .env.local')
  }
  
  return new GoogleGenerativeAI(apiKey)
}

export async function POST(request: NextRequest) {
  try {
    const config = getAIProvider()
    let formData
    try {
      formData = await request.formData()
    } catch (formError: any) {
      return NextResponse.json(
        { error: `Failed to parse form data: ${formError?.message || 'Unknown error'}` },
        { status: 400 }
      )
    }

    const file = formData.get('file') as File | null
    const code = formData.get('code') as string | null

    if (!file && !code) {
      return NextResponse.json(
        { error: 'Please provide either code or a file' },
        { status: 400 }
      )
    }

    // Prepare prompt
    const systemPrompt = `You are an expert code debugging assistant. When given code or error messages, you should:
1. Identify the error clearly
2. Explain why the error occurred
3. Provide a corrected version of the code

IMPORTANT: You MUST respond ONLY with valid JSON. Do not include any markdown, code blocks, or explanatory text outside the JSON.

Respond with a JSON object containing these exact keys:
- errorExplanation: A clear explanation of what the error is
- reasoning: A brief explanation of why the error happened
- fixedCode: The corrected code (if applicable, otherwise explain the fix)

Example format:
{"errorExplanation":"...","reasoning":"...","fixedCode":"..."}`

    let userPrompt = ''
    const parts: any[] = []
    
    // Handle file upload
    if (file) {
      try {
        const fileType = file.type || 'application/octet-stream'
        const fileContent = await file.arrayBuffer()
        const buffer = Buffer.from(fileContent)

        // Check file size
        const maxSize = fileType.startsWith('image/') ? 10 * 1024 * 1024 : 1024 * 1024
        if (buffer.length > maxSize) {
          return NextResponse.json(
            { error: `File is too large. Maximum size: ${maxSize / 1024 / 1024}MB` },
            { status: 400 }
          )
        }

        if (fileType.startsWith('image/')) {
          // For images, add to parts array for multimodal input
          const base64Image = buffer.toString('base64')
          parts.push({
            inlineData: {
              data: base64Image,
              mimeType: fileType,
            },
          })
          userPrompt = 'Please analyze this image for code errors. Identify any errors, explain why they occurred, and provide fixed code if applicable. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.'
        } else {
          // Handle text files
          const textContent = buffer.toString('utf-8')
          userPrompt = `Please analyze this code for errors:\n\n${textContent}\n\nIdentify any errors, explain why they occurred, and provide fixed code. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.`
        }
      } catch (fileError: any) {
        return NextResponse.json(
          { error: `Failed to process file: ${fileError?.message || 'Unknown error'}` },
          { status: 400 }
        )
      }
    }

    // Handle code input
    if (code && code.trim()) {
      userPrompt = `Please analyze this code for errors:\n\n${code}\n\nIdentify any errors, explain why they occurred, and provide fixed code. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.`
    }

    // Add text prompt to parts
    if (userPrompt) {
      parts.push({ text: `${systemPrompt}\n\n${userPrompt}` })
    }

    // Route to appropriate AI provider
    let content: string

    try {
      if (config.provider === 'gemini' && config.geminiApiKey) {
        // Use Gemini 2.5 Flash (free tier available)
        const genAI = getGeminiClient()
        const hasImage = file && file.type.startsWith('image/')
        
        // Use gemini-2.5-flash as per documentation
        const model = genAI.getGenerativeModel({ 
          model: 'gemini-2.5-flash',
          generationConfig: {
            temperature: 0.3,
          },
        })

        const result = await model.generateContent(parts)
        const response = result.response
        content = response.text()
      } else if (config.provider === 'ollama') {
        // Use Ollama (local, free)
        const fullPrompt = `${systemPrompt}\n\n${userPrompt}`
        const response = await fetch(`${config.ollamaUrl}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llama3.2:3b',
            prompt: fullPrompt,
            stream: false,
            options: { temperature: 0.3 },
          }),
        })

        if (!response.ok) {
          throw new Error(`Ollama API error: ${response.statusText}. Make sure Ollama is running: https://ollama.ai`)
        }

        const data = await response.json()
        content = data.response || ''
      } else if (config.provider === 'groq' && config.groqApiKey) {
        // Use Groq (free API, very fast)
        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${config.groqApiKey}`,
          },
          body: JSON.stringify({
            model: 'llama-3.1-8b-instant',
            messages: [
              { role: 'system', content: systemPrompt },
              { role: 'user', content: userPrompt },
            ],
            temperature: 0.3,
            response_format: { type: 'json_object' },
          }),
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(`Groq API error: ${errorData.error?.message || response.statusText}`)
        }

        const data = await response.json()
        content = data.choices[0]?.message?.content || ''
      } else {
        // Default: Try Gemini
        if (!config.geminiApiKey) {
          throw new Error('No AI provider configured. Please set GEMINI_API_KEY or choose another provider.')
        }
        const genAI = getGeminiClient()
        const model = genAI.getGenerativeModel({ 
          model: 'gemini-2.5-flash',
          generationConfig: { temperature: 0.3 },
        })
        const result = await model.generateContent(parts)
        content = result.response.text()
      }

      if (!content) {
        throw new Error('No response from AI')
      }

      // Parse JSON response
      let result
      try {
        result = JSON.parse(content)
      } catch (parseError) {
        // If JSON parsing fails, try to extract JSON from markdown code blocks
        const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*\})\s*```/) ||
          content.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          result = JSON.parse(jsonMatch[1] || jsonMatch[0])
        } else {
          // Fallback: create structured response from text
          result = {
            errorExplanation: content,
            reasoning: 'AI analysis completed',
            fixedCode: 'See explanation above',
          }
        }
      }

      // Ensure all required fields exist
      const debugResult = {
        errorExplanation: result.errorExplanation || result.explanation || 'No error explanation provided',
        reasoning: result.reasoning || result.reason || 'No reasoning provided',
        fixedCode: result.fixedCode || result.code || result.correctedCode || 'No fixed code provided',
      }

      return NextResponse.json(debugResult)
    } catch (aiError: any) {
      return NextResponse.json(
        {
          error: `AI Provider Error: ${aiError.message || 'Unknown error'}

Setup Instructions:
1. For Gemini 2.5 Flash (Recommended - Free tier available):
   - Get API key from: https://makersuite.google.com/app/apikey
   - Add to .env.local: GEMINI_API_KEY=your_key
   - Set: AI_PROVIDER=gemini (or leave default)

2. For Ollama (Free & Local):
   - Install from: https://ollama.ai
   - Run: ollama pull llama3.2:3b
   - Set: AI_PROVIDER=ollama

3. For Groq (Free API):
   - Get API key from: https://console.groq.com
   - Add to .env.local: GROQ_API_KEY=your_key
   - Set: AI_PROVIDER=groq`,
        },
        { status: 500 }
      )
    }
  } catch (error: any) {
    console.error('Debug API error:', error)

    return NextResponse.json(
      {
        error: error?.message || 'An unexpected error occurred',
        details: process.env.NODE_ENV === 'development' ? error?.stack : undefined,
      },
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
  }
}
