import { useState, useEffect } from 'react'
import api from '../services/api'

// Props: the parent (Dashboard) tells us which habit to show
interface CheckInCalendarProps {
  habitId: number
}

// Shape of a check-in from the backend
interface CheckIn {
  id: number
  habit_id: number
  check_in_date: string  // "2026-02-11"
  status: string
}

function CheckInCalendar({ habitId }: CheckInCalendarProps) {
  // Current month being displayed (defaults to today's month)
  const [currentDate, setCurrentDate] = useState(new Date())
  // Set of date strings for fast "did they check in?" lookups
  const [checkinDates, setCheckinDates] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  // Fetch check-ins whenever habitId changes
  useEffect(() => {
    const fetchCheckins = async () => {
      setLoading(true)
      try {
        const data: CheckIn[] = await api.checkins.getForHabit(habitId)
        // Build a Set of date strings like {"2026-02-01", "2026-02-03", ...}
        const dates = new Set(data.map((c: CheckIn) => c.check_in_date))
        setCheckinDates(dates)
      } catch {
        setCheckinDates(new Set())
      } finally {
        setLoading(false)
      }
    }
    fetchCheckins()
  }, [habitId])

  // ---- Calendar math ----
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth() // 0-indexed (0 = Jan, 1 = Feb, ...)

  // How many days in this month? (day 0 of next month = last day of this month)
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  // What day of the week does the 1st fall on? (0=Sun, 1=Mon, ..., 6=Sat)
  // We adjust so Monday = 0 (industry standard for calendars)
  const firstDayOfWeek = (new Date(year, month, 1).getDay() + 6) % 7

  // Month name for display
  const monthName = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })

  // Today's date string for highlighting
  const todayStr = new Date().toISOString().split('T')[0]

  // Navigate months
  const goToPrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }
  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  // Helper: format a day number into "2026-02-05" for Set lookup
  const formatDate = (day: number): string => {
    const m = String(month + 1).padStart(2, '0')
    const d = String(day).padStart(2, '0')
    return `${year}-${m}-${d}`
  }

  if (loading) {
    return <p className="text-gray-400 text-sm py-2">Loading calendar...</p>
  }

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      {/* Month navigation */}
      <div className="flex justify-between items-center mb-2">
        <button
          onClick={goToPrevMonth}
          className="text-gray-500 hover:text-gray-700 px-2 py-1 text-sm"
        >
          &lt; Prev
        </button>
        <span className="font-medium text-sm text-gray-700">{monthName}</span>
        <button
          onClick={goToNextMonth}
          className="text-gray-500 hover:text-gray-700 px-2 py-1 text-sm"
        >
          Next &gt;
        </button>
      </div>

      {/* Day-of-week headers */}
      <div className="grid grid-cols-7 gap-1 text-center text-xs text-gray-400 mb-1">
        <span>Mo</span>
        <span>Tu</span>
        <span>We</span>
        <span>Th</span>
        <span>Fr</span>
        <span>Sa</span>
        <span>Su</span>
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {/* Blank cells for days before the 1st */}
        {Array.from({ length: firstDayOfWeek }).map((_, i) => (
          <div key={`blank-${i}`} className="h-8" />
        ))}

        {/* Actual day cells */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1
          const dateStr = formatDate(day)
          const hasCheckin = checkinDates.has(dateStr)
          const isToday = dateStr === todayStr

          return (
            <div
              key={day}
              className={`h-8 flex items-center justify-center rounded text-xs font-medium
                ${hasCheckin
                  ? 'bg-green-400 text-white'
                  : 'bg-gray-100 text-gray-400'
                }
                ${isToday ? 'ring-2 ring-blue-400' : ''}
              `}
            >
              {day}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default CheckInCalendar
