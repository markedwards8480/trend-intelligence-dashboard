import { useState, useEffect } from 'react'
import { TrendItem } from '@/types'
import * as trendsApi from '@/api/trends'

export const useTrends = (params?: {
  category?: string
  platform?: string
  sort_by?: string
  limit?: number
  offset?: number
}) => {
  const [trends, setTrends] = useState<TrendItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await trendsApi.getDailyTrends(params)
        setTrends(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch trends')
      } finally {
        setLoading(false)
      }
    }

    fetchTrends()
  }, [params?.category, params?.platform, params?.sort_by, params?.limit, params?.offset])

  return { trends, loading, error }
}

export const useTrendById = (id: string) => {
  const [trend, setTrend] = useState<TrendItem | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    const fetchTrend = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await trendsApi.getTrendById(id)
        setTrend(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch trend')
      } finally {
        setLoading(false)
      }
    }

    fetchTrend()
  }, [id])

  return { trend, loading, error }
}
