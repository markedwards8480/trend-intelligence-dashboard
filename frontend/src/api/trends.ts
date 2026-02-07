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
  const response = await client.get<TrendItem[]>('/trends/daily', { params })
  return response.data
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
