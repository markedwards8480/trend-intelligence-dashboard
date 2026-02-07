import client from './client'
import { DashboardSummary } from '@/types'

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await client.get<DashboardSummary>('/dashboard/summary')
  return response.data
}
