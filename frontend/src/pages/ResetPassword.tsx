import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import api from '../services/api'

// Must match the backend rule in schemas/user.py (PasswordStr)
const MIN_PASSWORD_LENGTH = 8

function ResetPassword() {
  // The email link looks like /reset-password?token=eyJhbGci...
  // useSearchParams reads that query string for us.
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''

  // Form state
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Check locally first so an obvious mistake doesn't burn the token -
    // every submitted request consumes it whether or not it succeeds.
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters`)
      return
    }

    setLoading(true)

    try {
      await api.auth.resetPassword(token, password)
      setDone(true)

      // Give them a moment to read the confirmation, then send them to login
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      // The backend returns one generic message for expired, already-used,
      // and forged tokens - it deliberately won't say which.
      setError(err instanceof Error ? err.message : 'Reset failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-700">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <h1 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">StudySprint</h1>
        <p className="text-center text-gray-500 mb-6">Choose a new password</p>

        {/* Error message */}
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {!token ? (
          /* Someone opened this page directly, with no token in the URL */
          <div>
            <div className="bg-amber-100 text-amber-800 p-4 rounded mb-4">
              This reset link is missing its token. Open the link from your
              email, or request a new one.
            </div>
            <p className="text-center text-gray-600">
              <Link to="/forgot-password" className="text-blue-500 hover:underline">
                Request a new link
              </Link>
            </p>
          </div>
        ) : done ? (
          /* Success state */
          <div>
            <div className="bg-green-100 text-green-800 p-4 rounded mb-4">
              Password updated. Taking you to the login page...
            </div>
            <p className="text-center text-gray-600">
              <Link to="/login" className="text-blue-500 hover:underline">
                Go now
              </Link>
            </p>
          </div>
        ) : (
          /* Form state */
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">New password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={`At least ${MIN_PASSWORD_LENGTH} characters`}
                required
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 mb-2">Confirm password</label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type it again"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all duration-200"
            >
              {loading ? 'Updating...' : 'Update password'}
            </button>

            <p className="text-center mt-4 text-gray-600">
              <Link to="/login" className="text-blue-500 hover:underline">
                Back to login
              </Link>
            </p>
          </form>
        )}
      </div>
    </div>
  )
}

export default ResetPassword
