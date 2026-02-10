import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import HabitForm from '../components/HabitForm'

// TypeScript type for a Habit object (matches what backend returns)
interface Habit {
  id: number
  name: string
  description: string | null
  subject_tag: string | null
  goal_type: string
  target_frequency: number
  schedule_type: string
  is_active: boolean
  current_streak: number
  best_streak: number
  streak_status: string        // 'safe' | 'grace_used' | 'at_risk' | 'broken'
  grace_days_used: number
  grace_days_per_month: number
  grace_days_reset_date: string | null  // ISO date string from backend
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

  // Handle delete habit
  const handleDelete = async (habitId: number, habitName: string) => {
    if (!window.confirm(`Delete "${habitName}"? This cannot be undone.`)) {
      return
    }

    try {
      await api.habits.delete(habitId)
      refreshHabits()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
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
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-white">StudySprint</h1>
          <div className="flex gap-4 items-center">
            <Link to="/analytics" className="text-white/80 hover:text-white transition-colors">
              Analytics
            </Link>
            <button
              onClick={handleLogout}
              className="text-white/80 hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-4">Today's Habits</h2>

        {/* Grace day info banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6 text-sm text-blue-700">
          <p className="font-medium mb-1">How Grace Days Work</p>
          <p className="text-blue-600">
            Life happens! Each habit gets <strong>2 grace days per month</strong> —
            miss a day without breaking your streak. Grace days reset on the 1st of each month.
            Use them wisely to keep your streaks alive.
          </p>
        </div>

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
            className="bg-white p-4 rounded-xl shadow-md mb-3 hover:shadow-lg transition-shadow duration-200 border border-gray-100"
          >
            {/* Top row: name + action buttons */}
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-lg">{habit.name}</h3>
                {habit.description && (
                  <p className="text-gray-500 text-sm">{habit.description}</p>
                )}
              </div>

              <div className="flex gap-3 items-center">
                <button
                  onClick={() => handleCheckin(habit.id)}
                  className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors duration-200"
                >
                  Check In
                </button>
                <button
                  onClick={() => handleDelete(habit.id, habit.name)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            {/* Streak info row */}
            <div className="mt-3 flex flex-wrap gap-3 items-center text-sm">
              {/* Current streak */}
              <span className="font-semibold text-orange-500">
                {habit.current_streak} day streak
              </span>

              {/* Best streak */}
              <span className="text-gray-500">
                Best: {habit.best_streak} days
              </span>

              {/* Status badge */}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                habit.streak_status === 'safe'
                  ? 'bg-green-100 text-green-700'
                  : habit.streak_status === 'grace_used'
                  ? 'bg-yellow-100 text-yellow-700'
                  : habit.streak_status === 'at_risk'
                  ? 'bg-orange-100 text-orange-700'
                  : 'bg-red-100 text-red-700'
              }`}>
                {habit.streak_status === 'safe' && 'Safe'}
                {habit.streak_status === 'grace_used' && 'Grace Used'}
                {habit.streak_status === 'at_risk' && 'At Risk'}
                {habit.streak_status === 'broken' && 'Broken'}
              </span>

              {/* Grace days info */}
              <span className="text-gray-400">
                Grace: {habit.grace_days_used}/{habit.grace_days_per_month} used
              </span>

              {/* Grace reset date */}
              {habit.grace_days_reset_date && (
                <span className="text-gray-400">
                  Resets: {new Date(habit.grace_days_reset_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        ))}

        {/* Add new habit form */}
        <HabitForm onHabitCreated={refreshHabits} />
      </div>
    </div>
  )
}

export default Dashboard
