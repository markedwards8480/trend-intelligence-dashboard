import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import Sources from '@/pages/Sources'
import SubmitTrend from '@/pages/SubmitTrend'
import TrendDetail from '@/pages/TrendDetail'
import MoodBoards from '@/pages/MoodBoards'
import MoodBoardDetail from '@/pages/MoodBoardDetail'
import MonitoringCenter from '@/pages/MonitoringCenter'
import Analytics from '@/pages/Analytics'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/submit" element={<SubmitTrend />} />
        <Route path="/trends/:id" element={<TrendDetail />} />
        <Route path="/moodboards" element={<MoodBoards />} />
        <Route path="/moodboards/:id" element={<MoodBoardDetail />} />
        <Route path="/monitoring" element={<MonitoringCenter />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Layout>
  )
}
