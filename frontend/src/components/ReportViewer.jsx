import React from 'react'

export default function ReportViewer({ report }) {
  if (!report) {
    return <div className="empty-state">No report generated yet.</div>
  }

  return (
    <div className="report-viewer">
      <h2 className="report-title">{report.title}</h2>

      <div className="report-section">
        <h3>Executive Summary</h3>
        <p>{report.executive_summary}</p>
      </div>

      {(report.sections || []).map((section, idx) => (
        <div key={idx} className="report-section">
          <h3>{section.heading}</h3>
          <p>{section.content}</p>
        </div>
      ))}

      {(report.citations || []).length > 0 && (
        <div className="report-section">
          <h3>References</h3>
          <ul className="citations-list">
            {report.citations.map((cit, idx) => (
              <li key={idx}>{cit}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
