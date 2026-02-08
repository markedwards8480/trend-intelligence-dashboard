import client from './client'
import { Source, SourceCreate, SourceUpdate, SourceSuggestion } from '@/types'

export const getSources = async (params?: {
  platform?: string
  demographic?: string
  active?: boolean
}): Promise<Source[]> => {
  const response = await client.get<Source[]>('/sources', { params })
  return response.data
}

export const getSourceById = async (id: number): Promise<Source> => {
  const response = await client.get<Source>(`/sources/${id}`)
  return response.data
}

export const createSource = async (data: SourceCreate): Promise<Source> => {
  const response = await client.post<Source>('/sources', data)
  return response.data
}

export const updateSource = async (id: number, data: SourceUpdate): Promise<Source> => {
  const response = await client.put<Source>(`/sources/${id}`, data)
  return response.data
}

export const deleteSource = async (id: number): Promise<void> => {
  await client.delete(`/sources/${id}`)
}

export const analyzeFromSource = async (sourceId: number, url: string): Promise<any> => {
  const response = await client.post(`/sources/${sourceId}/analyze`, null, {
    params: { url },
  })
  return response.data
}

export const getSuggestions = async (): Promise<SourceSuggestion[]> => {
  const response = await client.post<SourceSuggestion[]>('/sources/suggestions')
  return response.data
}

export const createSourcesBulk = async (
  sources: SourceCreate[]
): Promise<{
  succeeded: number
  failed: Array<{ name: string; url: string; reason: string }>
}> => {
  const response = await client.post('/sources/bulk', { sources })
  return response.data
}
