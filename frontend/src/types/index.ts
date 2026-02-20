// ============ Demographics ============

export const DEMOGRAPHICS = ['junior_girls', 'young_women', 'contemporary', 'kids'] as const
export type Demographic = typeof DEMOGRAPHICS[number]

export const DEMOGRAPHIC_LABELS: Record<Demographic, string> = {
  junior_girls: 'Junior Girls (15-25)',
  young_women: 'Young Women (25-35)',
  contemporary: 'Contemporary (35+)',
  kids: 'Kids (6-14)',
}

export const DEMOGRAPHIC_SHORT_LABELS: Record<Demographic, string> = {
  junior_girls: 'Junior',
  young_women: 'Young Women',
  contemporary: 'Contemporary',
  kids: 'Kids',
}

// ============ Trend Items ============

export interface TrendItem {
  id: string
  url: string
  platform: string
  source_platform?: string
  category: string
  colors: string[]
  style_tags: string[]
  trend_score: number
  engagement_count: number
  likes?: number
  comments?: number
  shares?: number
  views?: number
  image_url?: string
  ai_analysis: string
  ai_analysis_text?: string
  created_at: string
  submitted_at?: string
  updated_at: string
  last_updated?: string
  // New fields
  demographic?: Demographic
  fabrications?: string[]
  source_id?: number
}

export interface TrendItemCreate {
  url: string
  platform: string
  source_id?: number
  demographic?: string
}

// ============ Sources ============

export interface Source {
  id: number
  url: string
  platform: string
  name: string
  target_demographics: Demographic[]
  frequency: string
  active: boolean
  trend_count: number
  last_scraped_at: string | null
  added_by: string
  added_at: string
}

export interface SourceCreate {
  url: string
  platform: string
  name: string
  target_demographics: string[]
  frequency: string
}

export interface SourceUpdate {
  active?: boolean
  name?: string
  target_demographics?: string[]
  frequency?: string
}

export interface SourceSuggestion {
  url: string
  platform: string
  name: string
  reasoning: string
  demographics: string[]
}

// ============ Social Media Discovery ============

export interface SocialAccount {
  platform: string
  handle: string
  url: string
  name: string
  type: string
  description: string
  estimated_followers: string
}

export interface BrandSocialDiscovery {
  brand: string
  accounts: SocialAccount[]
  related_influencers: SocialAccount[]
  hashtags: string[]
}

export interface SocialDiscoveryResponse {
  brands: BrandSocialDiscovery[]
  total_accounts: number
  total_influencers: number
}

// ============ Seed Generation ============

export interface SeedGenerationResponse {
  created: number
  skipped: number
  sources_processed: number
  errors: number
}

// ============ Mood Boards ============

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

// ============ Monitoring ============

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

// ============ Dashboard ============

export interface DashboardSummary {
  total_trends: number
  new_today: number
  top_category: string
  trending_color: string
  recent_trends: TrendItem[]
  category_breakdown: Record<string, number>
}

// ============ Metrics ============

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

// ============ Insights & Themed Looks ============

export interface TrendInsight {
  id: number
  category: string
  summary: string
  key_characteristics: {
    dominant_colors?: string[]
    dominant_styles?: string[]
    dominant_patterns?: string[]
    dominant_fabrications?: string[]
    price_trend?: string
  }
  trending_items_count: number
  avg_trend_score: number
  style_tags_distribution: Record<string, number>
  generated_at: string
}

export interface ThemedLook {
  id: number
  theme_name: string
  description: string
  color_palette: string[]
  key_items: Array<{ category: string; description: string }>
  style_tags: string[]
  mood_description: string | null
  demographic_appeal: string[]
  featured_trend_ids: number[] | null
  generated_at: string
}

export interface InsightsData {
  category_insights: TrendInsight[]
  themed_looks: ThemedLook[]
  generated_at: string | null
}

export interface InsightsStatus {
  status: 'idle' | 'running' | 'completed' | 'failed'
  progress: string | null
  started_at: string | null
  completed_at: string | null
  error: string | null
}
