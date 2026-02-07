export interface TrendItem {
  id: string
  url: string
  platform: string
  category: string
  colors: string[]
  style_tags: string[]
  trend_score: number
  engagement_count: number
  image_url?: string
  ai_analysis: string
  created_at: string
  updated_at: string
}

export interface TrendItemCreate {
  url: string
  platform: string
}

export interface MoodBoard {
  id: string
  title: string
  description: string
  created_by: string
  items: TrendItem[]
  created_at: string
  updated_at: string
}

export interface MoodBoardCreate {
  title: string
  description: string
}

export interface MonitoringTarget {
  id: string
  platform: string
  search_term: string
  is_active: boolean
  last_checked: string
  created_at: string
}

export interface MonitoringTargetCreate {
  platform: string
  search_term: string
}

export interface DashboardSummary {
  total_trends: number
  new_today: number
  top_category: string
  trending_color: string
  recent_trends: TrendItem[]
  category_breakdown: Record<string, number>
}

export interface TrendMetrics {
  trend_id: string
  engagement_over_time: Array<{
    date: string
    count: number
  }>
  platform_distribution: Record<string, number>
  color_frequency: Record<string, number>
  style_tag_frequency: Record<string, number>
}

export interface EngagementMetric {
  date: string
  likes: number
  comments: number
  shares: number
}

export interface TrendDetailResponse extends TrendItem {
  metrics?: TrendMetrics
  similar_items?: TrendItem[]
}
