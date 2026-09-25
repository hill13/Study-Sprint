import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

function ForgotPassword() {
  // Form state
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Once submitted we swap the form out for a confirmation message
  const [submitted, setSubmitted] = useState(false)

  // Only populated when the backend runs with EXPOSE_RESET_TOKEN=true
  // (local development). In production this stays null and the link arrives
  // by email instead.
  const [devToken, setDevToken] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await api.auth.forgotPassword(email)

      // NOTE: this succeeds even when no account has that email. The backend
      // returns an identical response either way so nobody can use this form
      // to discover which emails are registered. Do not "helpfully" tell the
      // user the address was not found - we genuinely do not know.
      setSubmitted(true)
      setDevToken(data.reset_token ?? null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-700">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <h1 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">StudySprint</h1>
        <p className="text-center text-gray-500 mb-6">Reset your password</p>

        {/* Error message */}
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {submitted ? (
          /* Confirmation state */
          <div>
            <div className="bg-green-100 text-green-800 p-4 rounded mb-4">
              If an account exists for <span className="font-semibold">{email}</span>,
              a reset link is on its way. The link expires in 15 minutes.
            </div>

            {/* Development shortcut - never rendered in production */}
            {devToken && (
              <div className="bg-amber-50 border border-amber-200 p-4 rounded mb-4">
                <p className="text-sm text-amber-900 mb-2 font-semibold">
                  Development mode
                </p>
                <p className="text-sm text-amber-900 mb-3">
                  Email is not configured, so here is the link directly:
                </p>
                <Link
                  to={`/reset-password?token=${devToken}`}
                  className="text-blue-600 hover:underline break-all text-sm"
                >
                  Continue to reset password
                </Link>
              </div>
            )}

            <p className="text-center text-gray-600">
              <Link to="/login" className="text-blue-500 hover:underline">
                Back to login
              </Link>
            </p>
          </div>
        ) : (
          /* Form state */
          <>
            <p className="text-gray-600 mb-6 text-sm">
              Enter the email you signed up with and we'll send you a link to
              choose a new password.
            </p>

            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all duration-200"
              >
                {loading ? 'Sending...' : 'Send reset link'}
              </button>
            </form>

            <p className="text-center mt-4 text-gray-600">
              Remembered it?{' '}
              <Link to="/login" className="text-blue-500 hover:underline">
                Back to login
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  )
}

export default ForgotPassword
