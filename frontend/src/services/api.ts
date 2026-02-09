/**
 * API Service
 *
 * Centralized API calls to the FastAPI backend.
 * All HTTP requests go through here.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// =============================================================================
// HELPER: Get stored auth token
// =============================================================================

function getToken(): string | null {
  return localStorage.getItem('token')
}

// =============================================================================
// HELPER: Make authenticated requests
// =============================================================================

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = getToken()

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // Add auth token if we have one
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  })

  // Handle errors
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Something went wrong' }))
    throw new Error(error.detail || 'Request failed')
  }

  // Return empty for 204 No Content
  if (response.status === 204) {
    return null
  }

  return response.json()
}

// =============================================================================
// AUTH ENDPOINTS
// =============================================================================

export const auth = {
  // Register a new user
  register: async (email: string, username: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    return response.json()
  },

  // Login and get token
  login: async (email: string, password: string) => {
    // FastAPI OAuth2 expects form data, not JSON
    const formData = new URLSearchParams()
    formData.append('username', email)  // OAuth2 uses 'username' field
    formData.append('password', password)

    const response = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    return response.json()  // Returns { access_token, token_type }
  },
}

// =============================================================================
// HABITS ENDPOINTS
// =============================================================================

export const habits = {
  // Get all habits for current user
  getAll: () => fetchWithAuth('/habits'),

  // Get a single habit
  getOne: (id: number) => fetchWithAuth(`/habits/${id}`),

  // Create a new habit
  create: (data: { name: string; description?: string; frequency?: string }) =>
    fetchWithAuth('/habits', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Update a habit
  update: (id: number, data: { name?: string; description?: string; frequency?: string }) =>
    fetchWithAuth(`/habits/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Delete a habit
  delete: (id: number) =>
    fetchWithAuth(`/habits/${id}`, {
      method: 'DELETE',
    }),
}

// =============================================================================
// CHECKINS ENDPOINTS
// =============================================================================

export const checkins = {
  // Get check-ins for a habit
  getForHabit: (habitId: number) =>
    fetchWithAuth(`/checkins?habit_id=${habitId}`),

  // Create a check-in (record completion)
  create: (data: { habit_id: number; status?: string; notes?: string; minutes_logged?: number }) =>
    fetchWithAuth('/checkins', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Delete a check-in
  delete: (id: number) =>
    fetchWithAuth(`/checkins/${id}`, {
      method: 'DELETE',
    }),
}

// =============================================================================
// ANALYTICS ENDPOINTS
// =============================================================================

export const analytics = {
  // Get all analytics data (weekly checkins, completion rate, streak comparison)
  getOverview: () => fetchWithAuth('/analytics/overview'),
}

// =============================================================================
// DEFAULT EXPORT
// =============================================================================

const api = { auth, habits, checkins, analytics }
export default api
