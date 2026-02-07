import client from './client'
import { MonitoringTarget, MonitoringTargetCreate } from '@/types'

export const getAllMonitoringTargets = async (): Promise<MonitoringTarget[]> => {
  const response = await client.get<MonitoringTarget[]>('/monitoring')
  return response.data
}

export const getMonitoringTargetById = async (id: string): Promise<MonitoringTarget> => {
  const response = await client.get<MonitoringTarget>(`/monitoring/${id}`)
  return response.data
}

export const createMonitoringTarget = async (data: MonitoringTargetCreate): Promise<MonitoringTarget> => {
  const response = await client.post<MonitoringTarget>('/monitoring', data)
  return response.data
}

export const updateMonitoringTarget = async (id: string, data: Partial<MonitoringTargetCreate>): Promise<MonitoringTarget> => {
  const response = await client.put<MonitoringTarget>(`/monitoring/${id}`, data)
  return response.data
}

export const deleteMonitoringTarget = async (id: string): Promise<void> => {
  await client.delete(`/monitoring/${id}`)
}

export const toggleMonitoringTarget = async (id: string, isActive: boolean): Promise<MonitoringTarget> => {
  const response = await client.patch<MonitoringTarget>(`/monitoring/${id}`, { is_active: isActive })
  return response.data
}
