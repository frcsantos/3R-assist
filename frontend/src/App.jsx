import { Navigate, Route, Routes } from 'react-router-dom'
import TopNav from './components/TopNav'
import { analyzeProtocol } from './lib/analyze'
import AdminPage from './pages/AdminPage'
import AnalyzePage from './pages/AnalyzePage'
import ExplorePage from './pages/ExplorePage'
import GlossaryPage from './pages/GlossaryPage'
import InfoPage from './pages/InfoPage'
import ParametersPage from './pages/ParametersPage'
import LiteratureSearchPage from './pages/LiteratureSearchPage'
import PubMedResultsPage from './pages/PubMedResultsPage'
import ResultsPage from './pages/ResultsPage'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav />
      <Routes>
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/admin/:section" element={<AdminPage />} />
        <Route path="/" element={<AnalyzePage onSubmit={analyzeProtocol} />} />
        <Route path="/parameters" element={<ParametersPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/explore/:section" element={<ExplorePage />} />
        <Route path="/resultados" element={<Navigate to="/results" replace />} />
        <Route path="/buscar" element={<Navigate to="/explore" replace />} />
        <Route path="/literature" element={<PubMedResultsPage />} />
        <Route path="/literature-search" element={<LiteratureSearchPage />} />
        <Route path="/glossary" element={<GlossaryPage />} />
        <Route path="/info" element={<InfoPage />} />
      </Routes>
    </div>
  )
}
