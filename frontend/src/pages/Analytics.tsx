import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'
import api from '../services/api'

// TypeScript types for analytics data
interface WeeklyCheckin {
  date: string
  day: string
  count: number
}

interface StreakComparison {
  name: string
  current_streak: number
  best_streak: number
}

interface AnalyticsData {
  weekly_checkins: WeeklyCheckin[]
  completion_rate: number
  streak_comparison: StreakComparison[]
}

function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Fetch analytics when page loads
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const result = await api.analytics.getOverview()
        setData(result)
      } catch (err) {
        setError('Failed to load analytics')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-500">Loading analytics...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top bar */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-white">Analytics</h1>
          <Link to="/dashboard" className="text-white/80 hover:text-white transition-colors">
            Back to Dashboard
          </Link>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-4xl mx-auto px-4 py-8">

        {/* Completion Rate */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6 border border-gray-100">
          <h2 className="text-lg font-bold mb-2">Completion Rate (30 days)</h2>
          <div className="flex items-center gap-4">
            <div className="text-4xl font-bold text-blue-500">
              {data?.completion_rate}%
            </div>
            <div className="flex-1 bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-500 h-4 rounded-full"
                style={{ width: `${Math.min(data?.completion_rate || 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Weekly Check-ins Bar Chart */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6 border border-gray-100">
          <h2 className="text-lg font-bold mb-4">Weekly Check-ins</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data?.weekly_checkins}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Streak Comparison */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6 border border-gray-100">
          <h2 className="text-lg font-bold mb-4">Streak Comparison</h2>
          {data?.streak_comparison.length === 0 ? (
            <p className="text-gray-500">No habits yet. Create some to see stats!</p>
          ) : (
            <ResponsiveContainer width="100%" height={data ? data.streak_comparison.length * 60 + 20 : 100}>
              <BarChart
                data={data?.streak_comparison}
                layout="vertical"
                margin={{ left: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="name" />
                <Tooltip />
                <Bar dataKey="current_streak" fill="#10B981" name="Current Streak" radius={[0, 4, 4, 0]} />
                <Bar dataKey="best_streak" fill="#F59E0B" name="Best Streak" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

      </div>
    </div>
  )
}

export default Analytics
