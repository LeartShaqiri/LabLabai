'use client'

import { useState } from 'react'

interface DebugResult {
  errorExplanation: string
  reasoning: string
  fixedCode: string
}

export default function Home() {
  const [code, setCode] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DebugResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleDebug = async () => {
    if (!code.trim() && !file) {
      setError('Please provide code or upload a file')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      
      if (file) {
        formData.append('file', file)
      }
      
      if (code.trim()) {
        formData.append('code', code)
      }

      const response = await fetch('/api/debug', {
        method: 'POST',
        body: formData,
      })

      // Check content type before parsing
      const contentType = response.headers.get('content-type')
      const isJson = contentType?.includes('application/json')

      if (!response.ok) {
        if (isJson) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Failed to debug code')
        } else {
          // If not JSON, it's likely an HTML error page
          const text = await response.text()
          throw new Error(`Server error (${response.status}): ${text.substring(0, 200)}`)
        }
      }

      if (!isJson) {
        throw new Error('Server returned non-JSON response')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>🔍 Smart Code Debugging Agent</h1>
      
      <div className="input-section">
        <div className="input-group">
          <label htmlFor="code-input">Paste your code or error message:</label>
          <textarea
            id="code-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here, or upload a file below..."
          />
        </div>

        <div className="input-group">
          <label>Upload screenshot, code file, or log file:</label>
          <div className="file-upload">
            <input
              type="file"
              id="file-input"
              accept="image/*,.txt,.log,.js,.ts,.jsx,.tsx,.py,.java,.cpp,.c,.cs,.rb,.go,.rs,.php"
              onChange={handleFileChange}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            />
            <label
              htmlFor="file-input"
              className={`file-upload-label ${isDragging ? 'dragover' : ''}`}
            >
              <div>
                <p>📁 Click to upload or drag and drop</p>
                <p style={{ fontSize: '0.85rem', color: '#999', marginTop: '0.5rem' }}>
                  Supports: Images, Code files, Log files
                </p>
              </div>
            </label>
          </div>
          {file && (
            <div className="file-info">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </div>
          )}
        </div>

        <button
          className="debug-button"
          onClick={handleDebug}
          disabled={loading || (!code.trim() && !file)}
        >
          {loading ? '🔄 Debugging...' : '🐛 Debug Code'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          <p>Analyzing your code with AI...</p>
        </div>
      )}

      {result && (
        <div className="result-section">
          <div className="result-title">✨ Debug Results</div>
          
          <div className="result-content">
            <h3>🔴 Error Explanation</h3>
            <p>{result.errorExplanation}</p>

            <h3>💭 Reasoning</h3>
            <p>{result.reasoning}</p>

            <h3>✅ Fixed Code</h3>
            <pre className="code-block">{result.fixedCode}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

