import { useState, useEffect, Component, ErrorInfo, ReactNode } from 'react'
import {
  TrendingUp, Hash, Palette, Eye, Heart, MessageCircle,
  Share2, ExternalLink, Filter, ChevronDown, ChevronUp,
  Sparkles, Users, Zap, BarChart3, Instagram, Globe,
  RefreshCw,
} from 'lucide-react'
import {
  getPostsFeed, getFeedStats, getTrendAnalysis,
  FeedPost, FeedStats, TrendAnalysis,
} from '@/api/feed'

const PLATFORM_ICONS: Record<string, string> = {
  instagram: 'IG',
  tiktok: 'TT',
  twitter: 'X',
  pinterest: 'Pin',
  youtube: 'YT',
}

const TYPE_COLORS: Record<string, string> = {
  celebrity: 'bg-purple-100 text-purple-700',
  influencer: 'bg-pink-100 text-pink-700',
  brand: 'bg-blue-100 text-blue-700',
  media: 'bg-amber-100 text-amber-700',
  stylist: 'bg-green-100 text-green-700',
  editor: 'bg-teal-100 text-teal-700',
}

const INSIGHT_ICONS: Record<string, string> = {
  style: '🎨',
  category: '👗',
  color: '🌈',
  convergence: '🔥',
  volume: '📊',
  info: 'ℹ️',
}

function formatNumber(n: any): string {
  if (n == null) return '0'
  const num = Number(n)
  if (isNaN(num)) return '0'
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return String(num)
}

// Safe array helper
function safeArr(val: any): any[] {
  return Array.isArray(val) ? val : []
}

// Error Boundary to catch rendering crashes
class FeedErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: string }> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false, error: '' }
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message }
  }
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Feed rendering error:', error, errorInfo)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="card p-8 text-center">
          <p className="text-red-600 font-bold mb-2">Something went wrong rendering the feed.</p>
          <p className="text-sm text-accent-500 mb-4">{this.state.error}</p>
          <button onClick={() => this.setState({ hasError: false, error: '' })} className="px-4 py-2 bg-primary-500 text-white rounded-lg">
            Try Again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

type Tab = 'insights' | 'feed'

export default function Feed() {
  const [tab, setTab] = useState<Tab>('insights')
  const [stats, setStats] = useState<FeedStats | null>(null)
  const [trends, setTrends] = useState<TrendAnalysis | null>(null)
  const [posts, setPosts] = useState<FeedPost[]>([])
  const [totalPosts, setTotalPosts] = useState(0)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [platform, setPlatform] = useState('')
  const [personType, setPersonType] = useState('')
  const [sortBy, setSortBy] = useState('engagement')
  const [days, setDays] = useState(7)

  const fetchAll = async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsData, trendsData, feedData] = await Promise.all([
        getFeedStats(days).catch(() => null),
        getTrendAnalysis({ days, min_mentions: 2 }).catch(() => null),
        getPostsFeed({
          platform: platform || undefined,
          person_type: personType || undefined,
          sort_by: sortBy,
          days,
          limit: 30,
          offset: 0,
        }).catch(() => ({ total: 0, posts: [], limit: 30, offset: 0 })),
      ])
      setStats(statsData)
      setTrends(trendsData)
      setPosts(feedData?.posts || [])
      setTotalPosts(feedData?.total || 0)
    } catch (err: any) {
      console.error('Failed to fetch feed:', err)
      setError(err?.message || 'Failed to load feed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [platform, personType, sortBy, days])

  const loadMore = async () => {
    setLoadingMore(true)
    try {
      const feedData = await getPostsFeed({
        platform: platform || undefined,
        person_type: personType || undefined,
        sort_by: sortBy,
        days,
        limit: 30,
        offset: posts.length,
      })
      setPosts([...posts, ...(feedData?.posts || [])])
    } catch (err) {
      console.error('Failed to load more:', err)
    } finally {
      setLoadingMore(false)
    }
  }

  return (
    <FeedErrorBoundary>
      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
          <div>
            <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">
              Trend Feed
            </h1>
            <p className="text-lg text-accent-600">
              Live insights from scraped posts across your people database
            </p>
          </div>
          <button
            onClick={fetchAll}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 mt-4 lg:mt-0 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800">
            {error}
          </div>
        )}

        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-8">
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-accent-900">{stats.total_posts || 0}</p>
              <p className="text-xs text-accent-500">Posts</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.unique_people_scraped || 0}</p>
              <p className="text-xs text-accent-500">People</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-pink-600">{formatNumber(stats.total_likes)}</p>
              <p className="text-xs text-accent-500">Total Likes</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-amber-600">{formatNumber(stats.total_comments)}</p>
              <p className="text-xs text-accent-500">Comments</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-purple-600">{formatNumber(stats.total_views)}</p>
              <p className="text-xs text-accent-500">Views</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.by_platform?.instagram || 0}</p>
              <p className="text-xs text-accent-500">IG Posts</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-accent-600">{stats.by_platform?.tiktok || 0}</p>
              <p className="text-xs text-accent-500">TT Posts</p>
            </div>
          </div>
        )}

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 mb-6 bg-accent-100 rounded-xl p-1 w-fit">
          <button
            onClick={() => setTab('insights')}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              tab === 'insights'
                ? 'bg-white text-accent-900 shadow-sm'
                : 'text-accent-500 hover:text-accent-700'
            }`}
          >
            <Sparkles className="w-4 h-4 inline mr-1.5" />
            Trend Insights
          </button>
          <button
            onClick={() => setTab('feed')}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              tab === 'feed'
                ? 'bg-white text-accent-900 shadow-sm'
                : 'text-accent-500 hover:text-accent-700'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-1.5" />
            Posts Feed
          </button>
        </div>

        {/* Filters Bar */}
        <div className="card p-4 mb-6">
          <div className="flex flex-wrap items-center gap-3">
            <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="input-base text-sm">
              <option value={3}>Last 3 days</option>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input-base text-sm">
              <option value="">All Platforms</option>
              <option value="instagram">Instagram</option>
              <option value="tiktok">TikTok</option>
              <option value="twitter">X / Twitter</option>
            </select>
            <select value={personType} onChange={(e) => setPersonType(e.target.value)} className="input-base text-sm">
              <option value="">All Types</option>
              <option value="celebrity">Celebrities</option>
              <option value="influencer">Influencers</option>
              <option value="brand">Brands</option>
              <option value="media">Media</option>
            </select>
            {tab === 'feed' && (
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="input-base text-sm">
                <option value="engagement">Sort: Engagement</option>
                <option value="recent">Sort: Most Recent</option>
                <option value="views">Sort: Most Views</option>
              </select>
            )}
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="card h-32 bg-gradient-to-br from-accent-50 to-accent-100 animate-pulse" />
            ))}
          </div>
        ) : tab === 'insights' ? (
          <InsightsView trends={trends} />
        ) : (
          <FeedView
            posts={posts}
            total={totalPosts}
            onLoadMore={loadMore}
            loadingMore={loadingMore}
          />
        )}
      </div>
    </FeedErrorBoundary>
  )
}


// ============ Insights View ============

function InsightsView({ trends }: { trends: TrendAnalysis | null }) {
  if (!trends || !trends.total_posts_analyzed) {
    return (
      <div className="card p-16 text-center">
        <Sparkles className="w-12 h-12 text-accent-300 mx-auto mb-4" />
        <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Posts Analyzed Yet</h3>
        <p className="text-accent-600">
          Go to the People page and scrape some profiles first, then come back here for trend insights.
        </p>
      </div>
    )
  }

  const insights = safeArr(trends.insights)
  const styles = safeArr(trends.trending_styles)
  const categories = safeArr(trends.trending_categories)
  const colors = safeArr(trends.trending_colors)
  const hashtags = safeArr(trends.trending_hashtags)
  const crossPerson = safeArr(trends.cross_person_trends)
  const topPosts = safeArr(trends.top_posts)

  return (
    <div className="space-y-6">
      {/* AI Insights Cards */}
      {insights.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {insights.map((insight: any, idx: number) => (
            <div key={idx} className="card p-5 border-l-4 border-primary-400">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{INSIGHT_ICONS[insight?.type] || '💡'}</span>
                <div>
                  <h4 className="font-bold text-accent-900 mb-1">{insight?.title || ''}</h4>
                  <p className="text-sm text-accent-600">{insight?.text || ''}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trending Styles */}
        {styles.length > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-pink-500" />
              Trending Styles
            </h3>
            <div className="space-y-2">
              {styles.map((s: any, idx: number) => (
                <div key={s?.term || idx} className="flex items-center justify-between py-2 border-b border-accent-50 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-accent-400 w-6">{idx + 1}</span>
                    <span className="text-sm font-medium text-accent-900">{s?.term || ''}</span>
                  </div>
                  <span className="text-sm px-2.5 py-0.5 bg-pink-50 text-pink-600 rounded-full font-medium">
                    {s?.count || 0} mentions
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trending Categories */}
        {categories.length > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              Hot Categories
            </h3>
            <div className="space-y-2">
              {categories.map((c: any, idx: number) => (
                <div key={c?.term || idx} className="flex items-center justify-between py-2 border-b border-accent-50 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-accent-400 w-6">{idx + 1}</span>
                    <span className="text-sm font-medium text-accent-900">{c?.term || ''}</span>
                  </div>
                  <span className="text-sm px-2.5 py-0.5 bg-blue-50 text-blue-600 rounded-full font-medium">
                    {c?.count || 0}x
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trending Colors */}
        {colors.length > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
              <Palette className="w-5 h-5 text-purple-500" />
              Color Trends
            </h3>
            <div className="flex flex-wrap gap-2">
              {colors.map((c: any) => (
                <span key={c?.term || Math.random()} className="text-sm px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full font-medium">
                  {c?.term || ''} ({c?.count || 0})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Trending Hashtags */}
        {hashtags.length > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
              <Hash className="w-5 h-5 text-amber-500" />
              Trending Hashtags
            </h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {hashtags.slice(0, 20).map((h: any) => (
                <div key={h?.hashtag || Math.random()} className="flex items-center justify-between py-2 border-b border-accent-50 last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-accent-900">#{h?.hashtag || ''}</span>
                    {h?.is_fashion_related && (
                      <span className="text-xs px-1.5 py-0.5 bg-green-50 text-green-600 rounded">fashion</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-accent-500">
                    <span>{h?.count || 0} posts</span>
                    <span>{h?.unique_people || 0} people</span>
                    <span className="text-pink-500">{formatNumber(h?.avg_engagement)} avg eng</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Cross-Person Convergence */}
      {crossPerson.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Cross-Person Trend Convergence
          </h3>
          <p className="text-sm text-accent-500 mb-4">
            Trends appearing across multiple people — strong signals for emerging directions.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {crossPerson.map((t: any, idx: number) => (
              <div key={idx} className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-accent-900">{t?.trend || ''}</span>
                  <span className="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded-full font-medium">
                    {t?.people_count || 0} people
                  </span>
                </div>
                <p className="text-xs text-accent-500">
                  {safeArr(t?.people).slice(0, 5).join(', ')}
                  {safeArr(t?.people).length > 5 && ` +${safeArr(t?.people).length - 5} more`}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Posts */}
      {topPosts.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-bold text-accent-900 mb-4 flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-500" />
            Top Posts by Engagement
          </h3>
          <div className="space-y-3">
            {topPosts.slice(0, 10).map((post: any, idx: number) => (
              <PostCard key={post?.id || idx} post={post || {}} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


// ============ Feed View ============

function FeedView({
  posts,
  total,
  onLoadMore,
  loadingMore,
}: {
  posts: FeedPost[]
  total: number
  onLoadMore: () => void
  loadingMore: boolean
}) {
  const safePosts = safeArr(posts)

  if (safePosts.length === 0) {
    return (
      <div className="card p-16 text-center">
        <BarChart3 className="w-12 h-12 text-accent-300 mx-auto mb-4" />
        <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Posts Yet</h3>
        <p className="text-accent-600">
          Scrape some people to populate the feed.
        </p>
      </div>
    )
  }

  return (
    <div>
      <p className="text-sm text-accent-500 mb-4">{total || 0} posts total</p>
      <div className="space-y-3">
        {safePosts.map((post: any, idx: number) => (
          <PostCard key={post?.id || idx} post={post || {}} />
        ))}
      </div>
      {safePosts.length < (total || 0) && (
        <div className="text-center mt-6">
          <button
            onClick={onLoadMore}
            disabled={loadingMore}
            className="px-6 py-3 text-sm font-medium bg-accent-100 hover:bg-accent-200 text-accent-700 rounded-xl transition-colors disabled:opacity-50"
          >
            {loadingMore ? 'Loading...' : `Load More (${(total || 0) - safePosts.length} remaining)`}
          </button>
        </div>
      )}
    </div>
  )
}


// ============ Post Card ============

function PostCard({ post }: { post: any }) {
  const [expanded, setExpanded] = useState(false)

  if (!post) return null

  const imageUrls = safeArr(post.image_urls)
  const hashtagsList = safeArr(post.hashtags)
  const likes = Number(post.likes) || 0
  const comments = Number(post.comments) || 0
  const views = Number(post.views) || 0
  const shares = Number(post.shares) || 0

  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex gap-4">
        {/* Image thumbnail */}
        {imageUrls.length > 0 && imageUrls[0] && (
          <a href={post.post_url || '#'} target="_blank" rel="noopener noreferrer" className="flex-shrink-0">
            <img
              src={imageUrls[0]}
              alt=""
              className="w-20 h-20 object-cover rounded-lg bg-accent-100"
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
            />
          </a>
        )}

        <div className="flex-1 min-w-0">
          {/* Top row */}
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="font-bold text-sm text-accent-900">{post.person_name || 'Unknown'}</span>
            {post.person_type && (
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[post.person_type] || 'bg-accent-100 text-accent-600'}`}>
                {post.person_type}
              </span>
            )}
            <span className="text-xs px-1.5 py-0.5 bg-accent-100 text-accent-600 rounded font-medium">
              {PLATFORM_ICONS[post.platform] || post.platform || '?'}
            </span>
            {post.posted_at && (
              <span className="text-xs text-accent-400">
                {new Date(post.posted_at).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Caption */}
          {post.caption && (
            <p
              className={`text-sm text-accent-600 mb-2 ${expanded ? '' : 'line-clamp-2'}`}
              onClick={() => setExpanded(!expanded)}
              style={{ cursor: 'pointer' }}
            >
              {post.caption}
            </p>
          )}

          {/* Hashtags */}
          {hashtagsList.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {hashtagsList.slice(0, expanded ? 50 : 5).map((tag: string, i: number) => (
                <span key={tag || i} className="text-xs px-1.5 py-0.5 bg-primary-50 text-primary-600 rounded">
                  #{tag}
                </span>
              ))}
              {!expanded && hashtagsList.length > 5 && (
                <span className="text-xs text-accent-400">+{hashtagsList.length - 5}</span>
              )}
            </div>
          )}

          {/* Engagement */}
          <div className="flex items-center gap-4 text-xs text-accent-500">
            <span className="flex items-center gap-1">
              <Heart className="w-3.5 h-3.5 text-pink-400" />
              {formatNumber(likes)}
            </span>
            <span className="flex items-center gap-1">
              <MessageCircle className="w-3.5 h-3.5 text-blue-400" />
              {formatNumber(comments)}
            </span>
            {views > 0 && (
              <span className="flex items-center gap-1">
                <Eye className="w-3.5 h-3.5 text-purple-400" />
                {formatNumber(views)}
              </span>
            )}
            {shares > 0 && (
              <span className="flex items-center gap-1">
                <Share2 className="w-3.5 h-3.5 text-green-400" />
                {formatNumber(shares)}
              </span>
            )}
            {post.post_url && (
              <a
                href={post.post_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-primary-500 hover:text-primary-700 ml-auto"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                View
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
