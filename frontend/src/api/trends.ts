import client from './client'
import { TrendItem, TrendItemCreate, TrendMetrics } from '@/types'

export const submitTrend = async (data: TrendItemCreate): Promise<TrendItem> => {
  const response = await client.post<TrendItem>('/trends/submit', data)
  return response.data
}

export const getDailyTrends = async (params?: {
  category?: string
  platform?: string
  sort_by?: string
  limit?: number
  offset?: number
}): Promise<TrendItem[]> => {
  const response = await client.get('/trends/daily', { params })
  // Backend returns { items: [...], total, limit, offset }
  const data = response.data
  const items = Array.isArray(data) ? data : (data.items || [])
  // Ensure IDs are strings for React keys
  return items.map((item: any) => ({ ...item, id: String(item.id) }))
}

export const getTrendById = async (id: string): Promise<TrendItem> => {
  const response = await client.get<TrendItem>(`/trends/${id}`)
  return response.data
}

export const reanalyzeTrend = async (id: string): Promise<TrendItem> => {
  const response = await client.post<TrendItem>(`/trends/${id}/analyze`, {})
  return response.data
}

export const getTrendMetrics = async (id: string): Promise<TrendMetrics> => {
  const response = await client.get<TrendMetrics>(`/trends/metrics/${id}`)
  return response.data
}
