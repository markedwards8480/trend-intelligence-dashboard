import client from './client'

// ============ Types ============

export interface PersonPlatform {
  id: number
  platform: string
  handle: string
  profile_url: string
  follower_count: number
  is_verified: boolean
  scrape_enabled: boolean
  last_checked: string | null
}

export interface Person {
  id: number
  name: string
  type: string
  tier: string | null
  bio: string | null
  primary_region: string | null
  secondary_regions: string[] | null
  demographics: string[] | null
  style_tags: string[] | null
  categories: string[] | null
  follower_count_total: number
  relevance_score: number
  active: boolean
  scrape_frequency: string
  priority: number
  notes: string | null
  last_scraped_at: string | null
  added_at: string
  platforms: PersonPlatform[]
}

export interface PersonStats {
  total_people: number
  by_type: Record<string, number>
  by_region: Record<string, number>
  by_tier: Record<string, number>
  total_platforms: number
  active_count: number
}

export interface ScrapedPost {
  id: number
  person_id: number
  platform: string
  post_url: string
  image_urls: string[]
  caption: string | null
  hashtags: string[]
  likes: number
  comments: number
  shares: number
  views: number
  analyzed: boolean
  ai_analysis: Record<string, any> | null
  scraped_at: string
  posted_at: string | null
}

// ============ API Functions ============

export const getPeopleStats = async (): Promise<PersonStats> => {
  const response = await client.get<PersonStats>('/people/stats')
  return response.data
}

export const listPeople = async (params?: {
  type?: string
  tier?: string
  region?: string
  platform?: string
  active?: boolean
  search?: string
  sort_by?: string
  limit?: number
  offset?: number
}): Promise<Person[]> => {
  const response = await client.get<Person[]>('/people', { params })
  return response.data
}

export const getPerson = async (id: number): Promise<Person> => {
  const response = await client.get<Person>(`/people/${id}`)
  return response.data
}

export const addPerson = async (data: {
  name: string
  type: string
  tier?: string
  bio?: string
  primary_region?: string
  platforms: Array<{
    platform: string
    handle: string
    follower_count?: number
  }>
}): Promise<Person> => {
  const response = await client.post<Person>('/people', data)
  return response.data
}

export const updatePerson = async (
  id: number,
  data: Partial<{
    name: string
    type: string
    tier: string
    bio: string
    primary_region: string
    active: boolean
    priority: number
    relevance_score: number
  }>
): Promise<Person> => {
  const response = await client.put<Person>(`/people/${id}`, data)
  return response.data
}

export const deletePerson = async (id: number): Promise<void> => {
  await client.delete(`/people/${id}`)
}

export const seedPeopleDatabase = async (): Promise<{
  message: string
  created: number
  skipped: number
  errors: Array<{ name: string; error: string }>
  total_in_seed: number
}> => {
  const response = await client.post('/people/seed')
  return response.data
}

export const scrapePerson = async (id: number): Promise<{
  status: string
  new_posts: number
  person: string
}> => {
  const response = await client.post(`/people/${id}/scrape`)
  return response.data
}

export const getPersonPosts = async (
  id: number,
  params?: { limit?: number; analyzed_only?: boolean }
): Promise<ScrapedPost[]> => {
  const response = await client.get<ScrapedPost[]>(`/people/${id}/posts`, { params })
  return response.data
}

export const scrapeBatch = async (params?: {
  type?: string
  region?: string
  priority_max?: number
  limit?: number
}): Promise<{
  total_people: number
  total_new_posts: number
  errors: Array<{ name: string; error: string }>
}> => {
  const response = await client.post('/people/scrape-batch', null, { params })
  return response.data
}
