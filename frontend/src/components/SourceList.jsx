import React from 'react'

export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) {
    return <div className="empty-state">No sources found.</div>
  }

  return (
    <div className="source-list">
      <h3>Sources ({sources.length})</h3>
      {sources.map((src, idx) => (
        <div key={idx} className="source-item">
          <a href={src.url} target="_blank" rel="noopener noreferrer" className="source-title">
            {src.title || src.url}
          </a>
          {src.snippet && <p className="source-snippet">{src.snippet}</p>}
          {src.relevance_score > 0 && (
            <span className="source-relevance">
              Relevance: {Math.round(src.relevance_score * 100)}%
            </span>
          )}
        </div>
      ))}
    </div>
  )
}
