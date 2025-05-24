import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import AnalysisTool from './AnalysisTool'
import History from './History'
import PopularStudies from './PopularStudies'

const App = () => {
  return (
    <div className="p-4 space-y-4">
      <nav className="space-x-4">
        <Link to="/">Анализ</Link>
        <Link to="/history">История</Link>
        <Link to="/popular">Популярное</Link>
      </nav>
      <Routes>
        <Route path="/" element={<AnalysisTool />} />
        <Route path="/history" element={<History />} />
        <Route path="/popular" element={<PopularStudies />} />
      </Routes>
    </div>
  )
}

export default App