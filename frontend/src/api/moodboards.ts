import client from './client'
import { MoodBoard, MoodBoardCreate } from '@/types'

export const getAllMoodBoards = async (): Promise<MoodBoard[]> => {
  const response = await client.get<MoodBoard[]>('/moodboards')
  return response.data
}

export const getMoodBoardById = async (id: string): Promise<MoodBoard> => {
  const response = await client.get<MoodBoard>(`/moodboards/${id}`)
  return response.data
}

export const createMoodBoard = async (data: MoodBoardCreate): Promise<MoodBoard> => {
  const response = await client.post<MoodBoard>('/moodboards', data)
  return response.data
}

export const updateMoodBoard = async (id: string, data: Partial<MoodBoardCreate>): Promise<MoodBoard> => {
  const response = await client.put<MoodBoard>(`/moodboards/${id}`, data)
  return response.data
}

export const deleteMoodBoard = async (id: string): Promise<void> => {
  await client.delete(`/moodboards/${id}`)
}

export const addItemToMoodBoard = async (boardId: string, trendId: string): Promise<MoodBoard> => {
  const response = await client.post<MoodBoard>(`/moodboards/${boardId}/items`, { trend_id: trendId })
  return response.data
}

export const removeItemFromMoodBoard = async (boardId: string, trendId: string): Promise<MoodBoard> => {
  const response = await client.delete<MoodBoard>(`/moodboards/${boardId}/items/${trendId}`)
  return response.data
}
