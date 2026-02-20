import { InsightsData, InsightsStatus } from '@/types'

const API = import.meta.env.VITE_API_URL || ''

export async function startInsightsGeneration(): Promise<{ message: string; status: string }> {
  const res = await fetch(`${API}/api/insights/generate`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start insights generation')
  return res.json()
}

export async function getInsightsStatus(): Promise<InsightsStatus> {
  const res = await fetch(`${API}/api/insights/status`)
  if (!res.ok) throw new Error('Failed to get insights status')
  return res.json()
}

export async function getInsights(demographic?: string): Promise<InsightsData> {
  const params = new URLSearchParams()
  if (demographic) params.set('demographic', demographic)
  const qs = params.toString()
  const res = await fetch(`${API}/api/insights${qs ? `?${qs}` : ''}`)
  if (!res.ok) throw new Error('Failed to get insights')
  return res.json()
}
