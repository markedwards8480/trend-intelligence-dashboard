import client from './client'

// --- Types ---

export interface FeedPost {
  id: number
  person_id: number
  person_name: string
  person_type: string
  person_tier: string | null
  platform: string
  post_url: string
  image_urls: string[]
  caption: string
  hashtags: string[]
  likes: number
  comments: number
  shares: number
  views: number
  engagement_rate: number
  posted_at: string | null
  scraped_at: string | null
  analyzed: boolean
  style_tags: string[]
  category: string | null
  ai_narrative: string | null
}

export interface FeedResponse {
  total: number
  limit: number
  offset: number
  posts: FeedPost[]
}

export interface FeedStats {
  period_days: number
  total_posts: number
  by_platform: Record<string, number>
  total_likes: number
  total_comments: number
  total_views: number
  unique_people_scraped: number
}

export interface TrendingHashtag {
  hashtag: string
  count: number
  total_likes: number
  total_comments: number
  unique_people: number
  avg_engagement: number
  is_fashion_related: boolean
}

export interface TrendTerm {
  term: string
  count: number
}

export interface CrossPersonTrend {
  trend: string
  type: string
  people_count: number
  people: string[]
}

export interface TrendInsight {
  type: string
  title: string
  text: string
}

export interface TopPost {
  id: number
  person_name: string
  person_type: string
  platform: string
  post_url: string
  image_urls: string[]
  caption: string
  hashtags: string[]
  likes: number
  comments: number
  shares: number
  views: number
  posted_at: string | null
  scraped_at: string | null
}

export interface TrendAnalysis {
  period_days: number
  total_posts_analyzed: number
  trending_hashtags: TrendingHashtag[]
  trending_styles: TrendTerm[]
  trending_categories: TrendTerm[]
  trending_colors: TrendTerm[]
  trending_patterns: TrendTerm[]
  trending_fabrics: TrendTerm[]
  top_posts: TopPost[]
  cross_person_trends: CrossPersonTrend[]
  insights: TrendInsight[]
}

// --- API Functions ---

export async function getPostsFeed(params: {
  platform?: string
  person_id?: number
  person_type?: string
  days?: number
  sort_by?: string
  limit?: number
  offset?: number
}): Promise<FeedResponse> {
  const { data } = await client.get('/feed/posts', { params })
  return data
}

export async function getFeedStats(days?: number): Promise<FeedStats> {
  const { data } = await client.get('/feed/stats', { params: { days } })
  return data
}

export async function getTrendAnalysis(params?: {
  days?: number
  min_mentions?: number
}): Promise<TrendAnalysis> {
  const { data } = await client.get('/feed/trends', { params })
  return data
}
