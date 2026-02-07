import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import HabitForm from '../components/HabitForm'

// TypeScript type for a Habit object (matches what backend returns)
interface Habit {
  id: number
  name: string
  description: string
  frequency: string
  current_streak: number
  longest_streak: number
}

function Dashboard() {
  // State
  const [habits, setHabits] = useState<Habit[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Hooks
  const { logout } = useAuth()
  const navigate = useNavigate()

  // Reusable function to fetch habits
  const refreshHabits = async () => {
    try {
      const data = await api.habits.getAll()
      setHabits(data)
    } catch (err) {
      setError('Failed to load habits')
    } finally {
      setLoading(false)
    }
  }

  // Fetch habits when page loads
  useEffect(() => {
    refreshHabits()
  }, [])

  // Handle logout
  const handleLogout = () => {
    logout()            // Clear token from AuthContext + localStorage
    navigate('/login')  // Redirect to login
  }

  // Handle check-in (mark habit as done today)
  const handleCheckin = async (habitId: number) => {
    try {
      await api.checkins.create({ habit_id: habitId })
      // Refresh habits to update streak
      const data = await api.habits.getAll()
      setHabits(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Check-in failed')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top bar */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">StudySprint</h1>
          <button
            onClick={handleLogout}
            className="text-red-500 hover:text-red-700"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">Today's Habits</h2>

        {/* Error message */}
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Loading state */}
        {loading && <p className="text-gray-500">Loading habits...</p>}

        {/* No habits yet */}
        {!loading && habits.length === 0 && (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <p className="text-gray-500 mb-4">No habits yet. Create your first one!</p>
          </div>
        )}

        {/* Habit list */}
        {habits.map((habit) => (
          <div
            key={habit.id}
            className="bg-white p-4 rounded-lg shadow mb-3 flex justify-between items-center"
          >
            {/* Habit info */}
            <div>
              <h3 className="font-bold text-lg">{habit.name}</h3>
              <p className="text-gray-500 text-sm">{habit.description}</p>
              <p className="text-orange-500 text-sm mt-1">
                {habit.current_streak} day streak
              </p>
            </div>

            {/* Check-in button */}
            <button
              onClick={() => handleCheckin(habit.id)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Check In
            </button>
          </div>
        ))}

        {/* Add new habit form */}
        <HabitForm onHabitCreated={refreshHabits} />
      </div>
    </div>
  )
}

export default Dashboard
