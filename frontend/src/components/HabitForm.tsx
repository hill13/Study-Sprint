import { useState } from 'react'
import api from '../services/api'

// Props type - what the parent (Dashboard) passes to this component
interface HabitFormProps {
  onHabitCreated: () => void  // Function to call after creating a habit
}

function HabitForm({ onHabitCreated }: HabitFormProps) {
  // Form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await api.habits.create({ name, description })

      // Clear form
      setName('')
      setDescription('')
      setShowForm(false)

      // Tell parent to refresh habit list
      onHabitCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create habit')
    } finally {
      setLoading(false)
    }
  }

  // If form is hidden, show the "Add" button
  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="w-full bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 mt-4"
      >
        + Add New Habit
      </button>
    )
  }

  // Show the form
  return (
    <div className="bg-white p-4 rounded-lg shadow mt-4">
      <h3 className="font-bold text-lg mb-3">New Habit</h3>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-3">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Habit name (e.g. Study Python)"
            required
          />
        </div>

        <div className="mb-3">
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Description (optional)"
          />
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-green-300"
          >
            {loading ? 'Creating...' : 'Create Habit'}
          </button>
          <button
            type="button"
            onClick={() => setShowForm(false)}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default HabitForm
