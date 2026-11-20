import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Experiments from './pages/Experiments'
import ExperimentDetail from './pages/ExperimentDetail'
import CreateExperiment from './pages/CreateExperiment'
import RunMonitor from './pages/RunMonitor'
import ResultsExplorer from './pages/ResultsExplorer'
import Datasets from './pages/Datasets'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/experiments" element={<Experiments />} />
        <Route path="/experiments/new" element={<CreateExperiment />} />
        <Route path="/experiments/:id" element={<ExperimentDetail />} />
        <Route path="/runs" element={<RunMonitor />} />
        <Route path="/results" element={<ResultsExplorer />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}
