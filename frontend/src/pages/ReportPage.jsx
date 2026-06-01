import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReportViewer from '../components/ReportViewer'
import { getResearch, exportReport } from '../api'

export default function ReportPage() {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [exported, setExported] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const result = await getResearch(taskId)
        setData(result)
      } catch (err) {
        alert(err.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [taskId])

  const handleExport = async (format) => {
    try {
      const result = await exportReport(taskId, format)
      setExported(result.content)
    } catch (err) {
      alert(err.message)
    }
  }

  if (loading) return <div className="page"><div className="loading">Loading report...</div></div>

  if (!data || !data.report) {
    return (
      <div className="page">
        <div className="empty-state">Report not found.</div>
        <button className="back-button" onClick={() => navigate('/')}>Back to Research</button>
      </div>
    )
  }

  return (
    <div className="page">
      <button className="back-button" onClick={() => navigate('/')}>Back to Research</button>

      <div className="export-actions">
        <button onClick={() => handleExport('markdown')}>Export Markdown</button>
        <button onClick={() => handleExport('text')}>Export Text</button>
      </div>

      {exported ? (
        <pre className="exported-content">{exported}</pre>
      ) : (
        <ReportViewer report={data.report} />
      )}

      {data.sources && <div className="sources-footer">
        <h3>Sources ({data.sources.length})</h3>
        <ul>
          {data.sources.map((s, i) => (
            <li key={i}><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title || s.url}</a></li>
          ))}
        </ul>
      </div>}
    </div>
  )
}
