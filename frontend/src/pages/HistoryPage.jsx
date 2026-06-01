import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'
import { listResearch, deleteResearch } from '../api'

export default function HistoryPage() {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchTasks = async () => {
    setLoading(true)
    try {
      const result = await listResearch()
      setTasks(result)
    } catch (err) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchTasks() }, [])

  const handleDelete = async (id) => {
    if (!confirm('Delete this research task?')) return
    try {
      await deleteResearch(id)
      setTasks(tasks.filter(t => t.id !== id))
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) return <div className="page"><div className="loading">Loading history...</div></div>

  return (
    <div className="page">
      <h2>Research History</h2>
      {tasks.length === 0 ? (
        <div className="empty-state">
          No research tasks yet.
          <button className="back-button" onClick={() => navigate('/')}>Start Research</button>
        </div>
      ) : (
        <div className="history-list">
          {tasks.map((task) => (
            <div key={task.id} className="history-item" onClick={() => navigate(`/report/${task.id}`)}>
              <div className="history-item-header">
                <h3>{task.topic}</h3>
                <ProgressBar status={task.status} progress={task.progress} />
              </div>
              <div className="history-item-meta">
                <span>{task.depth} depth</span>
                <span>{new Date(task.created_at).toLocaleDateString()}</span>
              </div>
              {task.error && <p className="error-text">{task.error}</p>}
              <button className="delete-button" onClick={(e) => { e.stopPropagation(); handleDelete(task.id) }}>
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
