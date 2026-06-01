import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBox from '../components/SearchBox'
import ProgressBar from '../components/ProgressBar'
import SourceList from '../components/SourceList'
import ReportViewer from '../components/ReportViewer'
import { startResearch, getResearch } from '../api'

export default function ResearchPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [task, setTask] = useState(null)
  const [polling, setPolling] = useState(null)

  const handleSearch = async (topic, depth) => {
    setLoading(true)
    setTask(null)
    if (polling) clearInterval(polling)

    try {
      const created = await startResearch(topic, depth)
      setTask(created)

      const interval = setInterval(async () => {
        try {
          const updated = await getResearch(created.id)
          setTask(updated)
          if (updated.task.status === 'completed' || updated.task.status === 'failed') {
            clearInterval(interval)
            setPolling(null)
            setLoading(false)
          }
        } catch {
          clearInterval(interval)
          setPolling(null)
          setLoading(false)
        }
      }, 2000)
      setPolling(interval)
    } catch (err) {
      setLoading(false)
      alert(err.message)
    }
  }

  return (
    <div className="page">
      <SearchBox onSearch={handleSearch} loading={loading} />
      {task && (
        <div className="results">
          <div className="task-header">
            <h2>{task.task?.topic || task.topic}</h2>
            <ProgressBar
              status={task.task?.status || task.status}
              progress={task.task?.progress || task.progress}
            />
          </div>
          {task.sources && <SourceList sources={task.sources} />}
          {task.report && <ReportViewer report={task.report} />}
          {task.task?.status === 'completed' && (
            <button className="view-report-btn" onClick={() => navigate(`/report/${task.task?.id || task.id}`)}>
              View Full Report
            </button>
          )}
        </div>
      )}
    </div>
  )
}
