import React, { useState } from 'react'

export default function SearchBox({ onSearch, loading }) {
  const [topic, setTopic] = useState('')
  const [depth, setDepth] = useState('medium')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (topic.trim() && !loading) {
      onSearch(topic.trim(), depth)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="search-box">
      <h2>What would you like to research?</h2>
      <div className="search-row">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a research topic..."
          disabled={loading}
          className="search-input"
        />
        <select value={depth} onChange={(e) => setDepth(e.target.value)} disabled={loading} className="depth-select">
          <option value="shallow">Shallow</option>
          <option value="medium">Medium</option>
          <option value="deep">Deep</option>
        </select>
        <button type="submit" disabled={loading || !topic.trim()} className="search-button">
          {loading ? 'Researching...' : 'Research'}
        </button>
      </div>
    </form>
  )
}
