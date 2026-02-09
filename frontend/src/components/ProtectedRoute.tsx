import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isLoggedIn } = useAuth()

  // Not logged in? Redirect to login
  if (!isLoggedIn) {
    return <Navigate to="/login" />
  }

  // Logged in? Show the page
  return children
}

export default ProtectedRoute
