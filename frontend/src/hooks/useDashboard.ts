import { useState, useEffect } from 'react'
import { DashboardSummary } from '@/types'
import * as dashboardApi from '@/api/dashboard'

export const useDashboard = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await dashboardApi.getDashboardSummary()
        setSummary(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard summary')
      } finally {
        setLoading(false)
      }
    }

    fetchSummary()
  }, [])

  return { summary, loading, error }
}
