import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Upload from './components/Upload'
import History from './components/History'
import Results from './components/Results'
import Stats from './components/Stats'
import { FileText, History as HistoryIcon, BarChart3, Home } from 'lucide-react'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-2">
                <FileText className="w-8 h-8 text-blue-600" />
                <span className="text-xl font-bold text-gray-800">SmartOCR Finance</span>
              </div>
              <div className="flex gap-4">
                <Link to="/" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                  <Home className="w-5 h-5" />
                  <span>Upload</span>
                </Link>
                <Link to="/history" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                  <HistoryIcon className="w-5 h-5" />
                  <span>Histórico</span>
                </Link>
                <Link to="/stats" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                  <BarChart3 className="w-5 h-5" />
                  <span>Estatísticas</span>
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/history" element={<History />} />
            <Route path="/results/:id" element={<Results />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
