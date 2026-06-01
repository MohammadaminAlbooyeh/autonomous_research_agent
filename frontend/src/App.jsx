import React from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import ResearchPage from './pages/ResearchPage'
import ReportPage from './pages/ReportPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <NavLink to="/" className="navbar-brand">Research Agent</NavLink>
        <div className="navbar-links">
          <NavLink to="/" end>Research</NavLink>
          <NavLink to="/history">History</NavLink>
        </div>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ResearchPage />} />
          <Route path="/report/:taskId" element={<ReportPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>
    </div>
  )
}
