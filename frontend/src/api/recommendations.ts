import client from './client'

export interface RecommendationItem {
  id: number
  type: string
  title: string
  description: string
  url: string
  platform: string
  reason: string
  confidence_score: number
  status: string
  created_at: string
}

export const getRecommendations = async (status?: string): Promise<RecommendationItem[]> => {
  const params: any = {}
  if (status) params.status = status
  const response = await client.get('/recommendations', { params })
  return response.data
}

export const generateRecommendations = async (): Promise<{ created: number; total_suggestions: number }> => {
  const response = await client.post('/recommendations/generate')
  return response.data
}

export const respondToRecommendation = async (
  id: number,
  status: 'accepted' | 'rejected' | 'dismissed'
): Promise<void> => {
  await client.post(`/recommendations/${id}/feedback`, { status })
}

export const submitTrendFeedback = async (
  trendId: number,
  feedbackType: 'thumbs_up' | 'thumbs_down'
): Promise<void> => {
  await client.post(`/recommendations/trends/${trendId}/feedback`, {
    feedback_type: feedbackType,
  })
}
