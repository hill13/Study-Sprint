import { useState } from 'react'

// import.meta.env  → Vite's way of reading environment variables (must start with VITE_)
// VITE_API_URL     → the backend URL set in frontend/.env
// || fallback      → use localhost if the variable isn't set (local development)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function AIInsights() {
  // Accumulated AI response text — starts empty, grows as chunks arrive
  // Why not replace? Because each chunk is just a few words — we append them
  const [insights, setInsights] = useState('')

  // True while waiting for the first chunk from the server
  // Used to show a "Thinking..." message so the user knows something is happening
  const [loading, setLoading] = useState(false)

  // Holds any error message (rate limit hit, network failure, no API key, etc.)
  const [error, setError] = useState('')

  const fetchInsights = async () => {
    // Part a: Reset state before every new request
    // Clear old insights so we don't append to a previous response
    setInsights('')
    setError('')
    setLoading(true)

    // Part b: Get the auth token from localStorage
    // Same place api.ts reads it — the token was saved on login
    // We attach it manually here because we're not using fetchWithAuth()
    const token = localStorage.getItem('token')

    try {
      // Part c: Call the backend with raw fetch() — NOT our api.ts helper
      // Why raw fetch()? Because api.ts uses response.json() which buffers
      // the full response. We need response.body (a ReadableStream) instead.
      // That's also why we manually add the Bearer token here.
      const response = await fetch(`${API_URL}/ai/insights`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`, // proves identity on this stateless request
          'Content-Type': 'application/json',
        },
      })

      // If server returned an error (e.g. 429 rate limit), parse and throw it
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Something went wrong')
      }

      // Part d: Get the ReadableStream from the response body
      // response.body is a pipe — bytes flow through it as Gemini writes them
      // .getReader() gives us a cursor to pull chunks from that pipe
      const reader = response.body!.getReader()

      // TextDecoder converts raw bytes (Uint8Array) → readable string
      // e.g. [89, 111, 117] → "You"
      const decoder = new TextDecoder()

      // Part e: Read chunks in a loop until the stream is done
      while (true) {
        // read() waits for the next available chunk from the server
        // done = true means Gemini finished and the stream is closed
        // value = the raw bytes of this chunk (Uint8Array)
        const { done, value } = await reader.read()

        if (done) break  // stream finished — exit the loop

        // Decode bytes → string
        // e.g. "data: You're doing great\n\ndata: with LeetCode!\n\n"
        const text = decoder.decode(value)

        // Split by "\n\n" to separate individual SSE events
        // One read() might return multiple events — network doesn't align to our boundaries
        const events = text.split('\n\n')

        for (const event of events) {
          if (!event.trim()) continue  // skip empty strings from trailing \n\n

          // Strip "data: " prefix — without this user would see "data: " on screen
          const content = event.replace('data: ', '')

          // Append this piece to the displayed text
          // prev => pattern: always reads the latest state to avoid losing chunks
          setInsights(prev => prev + content)
        }
      }
    } catch (err) {
      // Part g: Handle errors — rate limit, network failure, missing token, etc.
      setError(err instanceof Error ? err.message : 'Failed to get insights')
    } finally {
      // Part f: Always turn off loading — whether success or error
      setLoading(false)
    }
  }


  // ==========================================================================
  // STEP 12: JSX — button, loading state, insights panel, error message
  // ==========================================================================
  //
  // TODO: Build the UI
  //
  // Layout (same card style as Analytics page: bg-white rounded-xl shadow-md):
  //
  //   ┌─────────────────────────────────────────┐
  //   │  AI Study Coach                         │
  //   │                                         │
  //   │  [ Get AI Insights ]  ← button          │
  //   │                                         │
  //   │  Thinking...          ← if loading      │
  //   │                                         │
  //   │  1. You're doing great with...          │
  //   │  2. You could improve...        ← text  │
  //   │  3. Tomorrow, try...            panel   │
  //   │                                         │
  //   │  ● Error message      ← if error        │
  //   └─────────────────────────────────────────┘

  return <div />
}

export default AIInsights
