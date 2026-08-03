import { Route, Routes } from 'react-router-dom'
import TopNav from './components/TopNav'
import { analyzeProtocol } from './lib/analyze'
import AdminPage from './pages/AdminPage'
import AnalyzePage from './pages/AnalyzePage'
import GlossaryPage from './pages/GlossaryPage'
import InfoPage from './pages/InfoPage'
import ParametersPage from './pages/ParametersPage'
import LiteratureSearchPage from './pages/LiteratureSearchPage'
import PubMedResultsPage from './pages/PubMedResultsPage'
import ResultsPage from './pages/ResultsPage'
import SearchPage from './pages/SearchPage'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav />
      <Routes>
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/admin/:section" element={<AdminPage />} />
        <Route path="/" element={<AnalyzePage onSubmit={analyzeProtocol} />} />
        <Route path="/parameters" element={<ParametersPage />} />
        <Route path="/resultados" element={<ResultsPage />} />
        <Route path="/literature" element={<PubMedResultsPage />} />
        <Route path="/literature-search" element={<LiteratureSearchPage />} />
        <Route path="/buscar" element={<SearchPage />} />
        <Route path="/glossary" element={<GlossaryPage />} />
        <Route path="/info" element={<InfoPage />} />
      </Routes>
    </div>
  )
}
