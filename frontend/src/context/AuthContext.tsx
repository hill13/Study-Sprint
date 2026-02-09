import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'

// =============================================================================
// TYPES
// =============================================================================

interface AuthContextType {
  token: string | null
  isLoggedIn: boolean
  login: (token: string) => void
  logout: () => void
}

// =============================================================================
// CREATE CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextType | null>(null)

// =============================================================================
// PROVIDER - Wraps the app, provides auth state to all components
// =============================================================================

export function AuthProvider({ children }: { children: ReactNode }) {
  // Initialize token from localStorage (survives refresh)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))

  // Is the user logged in?
  const isLoggedIn = token !== null

  // Login: Save token to state + localStorage
  const login = (newToken: string) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)  // This triggers re-render for all listening components
  }

  // Logout: Remove token from state + localStorage
  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)  // This triggers re-render for all listening components
  }

  return (
    <AuthContext.Provider value={{ token, isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// =============================================================================
// HOOK - Easy way for components to access auth state
// =============================================================================

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
