import React from 'react'

export default function ProgressBar({ status, progress }) {
  if (status === 'pending' || status === 'in_progress') {
    return (
      <div className="progress-bar-container">
        <div className="progress-bar-label">
          {status === 'pending' ? 'Queued...' : 'Researching...'}
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{ width: `${Math.round((progress || 0) * 100)}%` }}
          />
        </div>
        <div className="progress-bar-percent">{Math.round((progress || 0) * 100)}%</div>
      </div>
    )
  }

  if (status === 'completed') {
    return <div className="status-badge status-completed">Completed</div>
  }

  if (status === 'failed') {
    return <div className="status-badge status-failed">Failed</div>
  }

  return null
}
