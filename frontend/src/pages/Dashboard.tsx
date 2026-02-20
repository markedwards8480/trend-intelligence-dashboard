import { useState, useEffect } from 'react'
import { TrendingUp, Zap, Palette, Heart, Sparkles, Check, X, RefreshCw, ExternalLink } from 'lucide-react'
import { useTrends } from '@/hooks/useTrends'
import TrendCard from '@/components/TrendCard'
import InsightsSection from '@/components/InsightsSection'
import { TrendItem, DEMOGRAPHICS, DEMOGRAPHIC_SHORT_LABELS, Demographic } from '@/types'
import { useNavigate } from 'react-router-dom'
import {
  getRecommendations,
  generateRecommendations,
  respondToRecommendation,
  RecommendationItem,
} from '@/api/recommendations'

export default function Dashboard() {
  const navigate = useNavigate()
  const [category, setCategory] = useState<string>('')
  const [platform, setPlatform] = useState<string>('')
  const [demographic, setDemographic] = useState<string>('')
  const [sortBy, setSortBy] = useState<string>('score')
  const [displayTrends, setDisplayTrends] = useState<TrendItem[]>([])

  // Recommendations state
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([])
  const [recsLoading, setRecsLoading] = useState(false)
  const [generatingRecs, setGeneratingRecs] = useState(false)

  const { trends: fetchedTrends, loading } = useTrends({ category, platform, demographic, sort_by: sortBy })
  // Unfiltered fetch for global stats
  const { trends: allTrends } = useTrends({ sort_by: 'score', limit: 500 })

  // Fetch recommendations on mount
  useEffect(() => {
    getRecommendations('pending').then(setRecommendations).catch(() => {})
  }, [])

  const handleGenerateRecs = async () => {
    setGeneratingRecs(true)
    try {
      await generateRecommendations()
      const recs = await getRecommendations('pending')
      setRecommendations(recs)
    } catch {
      // silently fail
    } finally {
      setGeneratingRecs(false)
    }
  }

  const handleRecResponse = async (id: number, status: 'accepted' | 'rejected') => {
    try {
      await respondToRecommendation(id, status)
      setRecommendations((prev) => prev.filter((r) => r.id !== id))
    } catch {
      // silently fail
    }
  }

  useEffect(() => {
    let filtered = [...fetchedTrends]

    if (sortBy === 'score') {
      filtered.sort((a, b) => (b.trend_score || 0) - (a.trend_score || 0))
    } else if (sortBy === 'engagement') {
      filtered.sort((a, b) => (b.engagement_count || 0) - (a.engagement_count || 0))
    } else if (sortBy === 'recent') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    }

    setDisplayTrends(filtered)
  }, [fetchedTrends, sortBy])

  // Compute dynamic stats from ALL data (not filtered)
  const totalTrends = allTrends.length
  const today = new Date().toISOString().split('T')[0]
  const newToday = allTrends.filter((t) => t.created_at?.startsWith(today)).length

  // Find the most common color
  const colorCounts: Record<string, number> = {}
  allTrends.forEach((t) => (t.colors || []).forEach((c) => { colorCounts[c] = (colorCounts[c] || 0) + 1 }))
  const trendingColor = Object.entries(colorCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'

  // Find the top category
  const catCounts: Record<string, number> = {}
  allTrends.forEach((t) => { if (t.category) catCounts[t.category] = (catCounts[t.category] || 0) + 1 })
  const topCategory = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'

  const stats = [
    {
      icon: TrendingUp,
      label: 'Total Trends Tracked',
      value: String(totalTrends),
      color: 'from-primary-400 to-primary-600',
    },
    {
      icon: Zap,
      label: 'New Today',
      value: String(newToday),
      color: 'from-orange-400 to-orange-600',
    },
    {
      icon: Palette,
      label: 'Trending Color',
      value: trendingColor,
      color: 'from-pink-300 to-pink-500',
    },
    {
      icon: Heart,
      label: 'Top Category',
      value: topCategory,
      color: 'from-red-400 to-red-600',
    },
  ]

  const categories = ['All', 'Dresses', 'Tops', 'Pants', 'Accessories', 'Footwear', 'Outfits']
  const platforms = ['All', 'ecommerce', 'social', 'media', 'search']
  const platformLabels: Record<string, string> = {
    'All': 'All Sources',
    'ecommerce': 'Ecommerce',
    'social': 'Social Media',
    'media': 'Fashion Media',
    'search': 'Search & Trends',
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">
          Trend Intelligence
        </h1>
        <p className="text-lg text-accent-600">
          Real-time fashion insights{demographic ? ` for ${DEMOGRAPHIC_SHORT_LABELS[demographic as Demographic]}` : ' across all demographics'}
        </p>
      </div>

      {/* Demographic Filter Pills */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setDemographic('')}
          className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
            !demographic
              ? 'bg-primary-600 text-white border-primary-600'
              : 'bg-white text-accent-600 border-accent-200 hover:border-primary-300'
          }`}
        >
          All Demographics
        </button>
        {DEMOGRAPHICS.map((demo) => (
          <button
            key={demo}
            onClick={() => setDemographic(demographic === demo ? '' : demo)}
            className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
              demographic === demo
                ? 'bg-primary-600 text-white border-primary-600'
                : 'bg-white text-accent-600 border-accent-200 hover:border-primary-300'
            }`}
          >
            {DEMOGRAPHIC_SHORT_LABELS[demo]}
          </button>
        ))}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {stats.map((stat, idx) => {
          const Icon = stat.icon
          return (
            <div key={idx} className="card overflow-hidden">
              <div className={`bg-gradient-to-br ${stat.color} p-4 flex items-center justify-center`}>
                <Icon className="w-8 h-8 text-white" />
              </div>
              <div className="p-6">
                <p className="text-sm text-accent-600 font-medium mb-2">{stat.label}</p>
                <p className="text-3xl font-display font-bold text-accent-900">{stat.value}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* AI Insights Section */}
      <InsightsSection
        demographic={demographic}
        onFilterByCategory={(cat) => {
          setCategory(cat)
          // Scroll down to trends grid
          document.getElementById('trends-grid')?.scrollIntoView({ behavior: 'smooth' })
        }}
        onFilterByStyleTags={(tags) => {
          // Clear other filters and let the style-tag-filtered trends show
          setCategory('')
          setPlatform('')
          setSortBy('score')
          // For now, scroll to grid — style tag filtering would need additional state
          document.getElementById('trends-grid')?.scrollIntoView({ behavior: 'smooth' })
        }}
      />

      {/* Filters */}
      <div className="card p-6 mb-8" id="trends-grid">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-accent-900 mb-2">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="input-base"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat === 'All' ? '' : cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Platform Filter */}
          <div>
            <label className="block text-sm font-medium text-accent-900 mb-2">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="input-base"
            >
              {platforms.map((plat) => (
                <option key={plat} value={plat === 'All' ? '' : plat}>
                  {platformLabels[plat] || plat}
                </option>
              ))}
            </select>
          </div>

          {/* Sort Filter */}
          <div>
            <label className="block text-sm font-medium text-accent-900 mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-base"
            >
              <option value="score">Trend Score</option>
              <option value="engagement">Engagement</option>
              <option value="recent">Most Recent</option>
            </select>
          </div>
        </div>
      </div>

      {/* AI Recommendations Section */}
      {recommendations.length > 0 && (
        <div className="card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-500" />
              <h2 className="text-lg font-display font-bold text-accent-900">Recommended for You</h2>
              <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-medium">AI</span>
            </div>
            <button
              onClick={handleGenerateRecs}
              disabled={generatingRecs}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
            >
              <RefreshCw className={`w-4 h-4 ${generatingRecs ? 'animate-spin' : ''}`} />
              {generatingRecs ? 'Generating...' : 'Get More'}
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.slice(0, 6).map((rec) => (
              <div key={rec.id} className="border border-accent-100 rounded-xl p-4 hover:border-primary-200 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-accent-900 text-sm truncate">{rec.title}</h3>
                    <span className="inline-block text-xs bg-accent-50 text-accent-600 px-2 py-0.5 rounded mt-1 capitalize">
                      {rec.platform}
                    </span>
                  </div>
                  <span className="text-xs font-bold text-primary-600 ml-2 shrink-0">
                    {Math.round(rec.confidence_score * 100)}%
                  </span>
                </div>
                {rec.description && (
                  <p className="text-xs text-accent-500 mb-2 line-clamp-2">{rec.description}</p>
                )}
                <p className="text-xs text-primary-600 mb-3 italic line-clamp-2">{rec.reason}</p>
                <div className="flex items-center gap-2">
                  <a
                    href={rec.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-accent-500 hover:text-primary-600 flex items-center gap-1"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Visit
                  </a>
                  <div className="flex-1" />
                  <button
                    onClick={() => handleRecResponse(rec.id, 'accepted')}
                    className="p-1.5 rounded-lg bg-green-50 text-green-600 hover:bg-green-100 transition-colors"
                    title="Accept — add to sources"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleRecResponse(rec.id, 'rejected')}
                    className="p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
                    title="Reject"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generate Recommendations prompt (when none exist) */}
      {recommendations.length === 0 && !loading && fetchedTrends.length > 0 && (
        <div className="card p-6 mb-8 border-dashed border-2 border-accent-200 bg-accent-50/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-primary-400" />
              <div>
                <h3 className="font-semibold text-accent-800 text-sm">Discover New Sources</h3>
                <p className="text-xs text-accent-500">Let AI suggest brands, influencers, and trends based on your data</p>
              </div>
            </div>
            <button
              onClick={handleGenerateRecs}
              disabled={generatingRecs}
              className="btn-primary text-sm px-4 py-2"
            >
              {generatingRecs ? (
                <span className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Get Recommendations
                </span>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Trends Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, idx) => (
            <div key={idx} className="card h-96 bg-gradient-to-br from-accent-50 to-accent-100 animate-pulse" />
          ))}
        </div>
      ) : displayTrends.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {displayTrends.map((trend) => (
            <TrendCard
              key={trend.id}
              trend={trend}
              onViewDetail={(id) => navigate(`/trends/${id}`)}
              onAddToMoodBoard={(trend) => {
                alert(`Added "${trend.category}" to mood board!`)
              }}
            />
          ))}
        </div>
      ) : (
        <div className="card p-16 text-center">
          <div className="text-5xl mb-4">👗</div>
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Trends Yet</h3>
          <p className="text-accent-600 mb-6">
            {category || platform
              ? 'No trends match your filters. Try adjusting them or submit new trends.'
              : 'Start by submitting fashion URLs to track and analyze trends.'}
          </p>
          <div className="flex gap-3 justify-center">
            {(category || platform) && (
              <button
                onClick={() => {
                  setCategory('')
                  setPlatform('')
                  setSortBy('score')
                }}
                className="btn-secondary"
              >
                Reset Filters
              </button>
            )}
            <button
              onClick={() => navigate('/submit')}
              className="btn-primary"
            >
              Submit a Trend
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
