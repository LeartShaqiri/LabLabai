import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

// Configure route for file uploads
export const runtime = 'nodejs'
export const maxDuration = 30

// Initialize Gemini client safely
function getGeminiClient() {
  const apiKey = process.env.GEMINI_API_KEY
  
  if (!apiKey) {
    // Check if it might be in a different variable name
    const altKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_KEY
    
    if (altKey) {
      console.warn('Found API key in alternative variable. Using it, but GEMINI_API_KEY is recommended.')
      return new GoogleGenerativeAI(altKey)
    }
    
    const errorMsg = `Gemini API key is not configured. 
Please create a .env.local file in the root directory with:
GEMINI_API_KEY=your_api_key_here

Then restart your dev server (npm run dev).

Get your API key from: https://makersuite.google.com/app/apikey`
    
    throw new Error(errorMsg)
  }
  
  // Validate API key format (Gemini keys typically start with "AIza")
  if (apiKey.length < 30 || (!apiKey.startsWith('AIza') && process.env.NODE_ENV === 'development')) {
    console.warn('Warning: API key format may be incorrect. Gemini API keys typically start with "AIza"')
  }
  
  return new GoogleGenerativeAI(apiKey)
}

export async function POST(request: NextRequest) {
  try {
    // Check for API key and initialize client
    let genAI
    try {
      genAI = getGeminiClient()
    } catch (initError: any) {
      return NextResponse.json(
        { error: initError.message || 'Failed to initialize Gemini client' },
        { status: 500 }
      )
    }

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

    // Prepare prompt for Gemini
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
{"errorExplanation":"...","reasoning":"...","fixedCode":"..."}

If the input is an image, analyze it carefully for code or error messages.`

    // Get the model - try different model name formats
    const hasImage = file && file.type.startsWith('image/')
    
    // Try model names in order of preference
    // Some API keys may have different model names available
    const modelNamesToTry = [
      'gemini-1.5-flash',
      'gemini-1.5-pro', 
      'gemini-pro',
    ]
    
    // Start with the first model
    let currentModelIndex = 0
    let model = genAI.getGenerativeModel({ 
      model: modelNamesToTry[currentModelIndex],
      generationConfig: {
        temperature: 0.3,
      },
    })
    let modelName = modelNamesToTry[currentModelIndex]

    // Build the prompt
    let userPrompt = systemPrompt + '\n\n'
    const parts: any[] = []

    // Handle file upload (image or text file)
    if (file) {
      try {
        const fileType = file.type || 'application/octet-stream'
        const fileContent = await file.arrayBuffer()
        const buffer = Buffer.from(fileContent)

        // Check file size (limit to 10MB for images, 1MB for text)
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
          const mimeType = fileType

          parts.push({
            inlineData: {
              data: base64Image,
              mimeType: mimeType,
            },
          })

          userPrompt += 'Please analyze this image for code errors. Identify any errors, explain why they occurred, and provide fixed code if applicable. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.'
        } else {
          // Handle text files
          const textContent = buffer.toString('utf-8')
          userPrompt += `Please analyze this code for errors:\n\n${textContent}\n\nIdentify any errors, explain why they occurred, and provide fixed code. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.`
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
      userPrompt += `Please analyze this code for errors:\n\n${code}\n\nIdentify any errors, explain why they occurred, and provide fixed code. Respond in JSON format with errorExplanation, reasoning, and fixedCode fields.`
    }

    // Add text prompt to parts (always add text at the end)
    parts.push({ text: userPrompt })

    // Call Gemini API - try different models if one fails
    let response
    let lastError: any = null
    
    for (let attempt = 0; attempt < modelNamesToTry.length; attempt++) {
      try {
        const result = await model.generateContent(parts)
        response = result.response
        break // Success, exit the loop
      } catch (geminiError: any) {
        lastError = geminiError
        const errorMessage = geminiError?.message || 'Gemini API error'
        
        // If it's a 404 (model not found), try the next model
        if ((errorMessage.includes('not found') || errorMessage.includes('404')) && attempt < modelNamesToTry.length - 1) {
          currentModelIndex++
          modelName = modelNamesToTry[currentModelIndex]
          model = genAI.getGenerativeModel({ 
            model: modelName,
            generationConfig: {
              temperature: 0.3,
            },
          })
          continue // Try next model
        }
        
        // If it's not a 404 or we've tried all models, return error
        const errorStatus = geminiError?.status || 500
        
        // Provide helpful message for model not found errors
        let helpfulMessage = errorMessage
        if (errorMessage.includes('not found') || errorMessage.includes('404')) {
          helpfulMessage = `None of the available Gemini models worked with your API key.
          
Tried models: ${modelNamesToTry.join(', ')}

This usually means:
1. Your API key doesn't have access to these models
2. The Generative Language API is not enabled in your Google Cloud project
3. Your API key may be restricted

Please:
- Check your API key at: https://makersuite.google.com/app/apikey
- Enable "Generative Language API" in Google Cloud Console
- Verify your API key has the correct permissions

Original error: ${errorMessage}`
        }

        return NextResponse.json(
          {
            error: `Gemini API error: ${helpfulMessage}`,
            details: process.env.NODE_ENV === 'development' ? geminiError?.stack : undefined,
          },
          { status: errorStatus >= 400 && errorStatus < 600 ? errorStatus : 500 }
        )
      }
    }
    
    if (!response) {
      return NextResponse.json(
        {
          error: `Failed to get response from any Gemini model.
          
Tried all models: ${modelNamesToTry.join(', ')}
Last error: ${lastError?.message || 'Unknown error'}

Please check your API key permissions and ensure the Generative Language API is enabled.`,
        },
        { status: 500 }
      )
    }

    const content = response.text()
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
  } catch (error: any) {
    console.error('Debug API error:', error)

    // Ensure we always return JSON, never HTML
    const errorMessage = error?.message || 'An unexpected error occurred'
    const errorStack = process.env.NODE_ENV === 'development' ? error?.stack : undefined

    return NextResponse.json(
      {
        error: errorMessage,
        details: errorStack,
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
