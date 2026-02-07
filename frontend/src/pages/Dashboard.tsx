import { useState, useEffect } from 'react'
import { TrendingUp, Zap, Palette, Heart } from 'lucide-react'
import { useTrends } from '@/hooks/useTrends'
import TrendCard from '@/components/TrendCard'
import { TrendItem } from '@/types'
import { useNavigate } from 'react-router-dom'

const mockTrends: TrendItem[] = [
  {
    id: '1',
    url: 'https://instagram.com/p/abc123',
    platform: 'Instagram',
    category: 'Dresses',
    colors: ['pink', 'white', 'beige'],
    style_tags: ['Y2K', 'Maxi', 'Summer'],
    trend_score: 92,
    engagement_count: 145000,
    image_url: undefined,
    ai_analysis: 'This Y2K-inspired maxi dress is trending across influencer circles. The pink and white color combination appeals to the junior demographic.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    url: 'https://tiktok.com/video/def456',
    platform: 'TikTok',
    category: 'Tops',
    colors: ['black', 'white'],
    style_tags: ['Crop Top', 'Mesh', 'Edgy'],
    trend_score: 87,
    engagement_count: 234000,
    image_url: undefined,
    ai_analysis: 'Mesh crop tops with minimalist styling are gaining momentum. High engagement from fashion creators.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    url: 'https://instagram.com/p/ghi789',
    platform: 'Instagram',
    category: 'Accessories',
    colors: ['gold', 'pink'],
    style_tags: ['Jewelry', 'Statement', 'Luxury'],
    trend_score: 78,
    engagement_count: 98000,
    image_url: undefined,
    ai_analysis: 'Gold statement jewelry is making a comeback with a modern twist. Perfect for layering.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    url: 'https://shein.com/product/jkl012',
    platform: 'SHEIN',
    category: 'Pants',
    colors: ['pink', 'purple'],
    style_tags: ['Cargo', 'Baggy', 'Streetwear'],
    trend_score: 85,
    engagement_count: 167000,
    image_url: undefined,
    ai_analysis: 'Cargo pants in unconventional colors are trending. Baggy silhouettes continue to dominate.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '5',
    url: 'https://fashionova.com/p/mno345',
    platform: 'Fashion Nova',
    category: 'Outfits',
    colors: ['black', 'white', 'beige'],
    style_tags: ['Bodysuit', 'Sexy', 'Monochrome'],
    trend_score: 81,
    engagement_count: 212000,
    image_url: undefined,
    ai_analysis: 'Monochromatic bodysuits are essential for current fashion. High engagement from the target demographic.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '6',
    url: 'https://instagram.com/p/pqr678',
    platform: 'Instagram',
    category: 'Footwear',
    colors: ['white', 'pink', 'purple'],
    style_tags: ['Sneakers', 'Platform', 'Chunky'],
    trend_score: 76,
    engagement_count: 123000,
    image_url: undefined,
    ai_analysis: 'Platform sneakers continue to gain traction. Color combinations matter significantly.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const [category, setCategory] = useState<string>('')
  const [platform, setPlatform] = useState<string>('')
  const [sortBy, setSortBy] = useState<string>('score')
  const [displayTrends, setDisplayTrends] = useState<TrendItem[]>(mockTrends)

  const { trends: fetchedTrends, loading } = useTrends({ category, platform, sort_by: sortBy })

  useEffect(() => {
    const finalTrends = fetchedTrends.length > 0 ? fetchedTrends : mockTrends

    let filtered = [...finalTrends]
    if (category) {
      filtered = filtered.filter((t) => t.category === category)
    }
    if (platform) {
      filtered = filtered.filter((t) => t.platform === platform)
    }

    if (sortBy === 'score') {
      filtered.sort((a, b) => b.trend_score - a.trend_score)
    } else if (sortBy === 'engagement') {
      filtered.sort((a, b) => b.engagement_count - a.engagement_count)
    } else if (sortBy === 'recent') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    }

    setDisplayTrends(filtered)
  }, [fetchedTrends, category, platform, sortBy])

  const stats = [
    {
      icon: TrendingUp,
      label: 'Total Trends Tracked',
      value: '2,847',
      color: 'from-primary-400 to-primary-600',
    },
    {
      icon: Zap,
      label: 'New Today',
      value: '23',
      color: 'from-orange-400 to-orange-600',
    },
    {
      icon: Palette,
      label: 'Trending Color',
      value: 'Soft Pink',
      color: 'from-pink-300 to-pink-500',
    },
    {
      icon: Heart,
      label: 'Top Category',
      value: 'Dresses',
      color: 'from-red-400 to-red-600',
    },
  ]

  const categories = ['All', 'Dresses', 'Tops', 'Pants', 'Accessories', 'Footwear', 'Outfits']
  const platforms = ['All', 'Instagram', 'TikTok', 'SHEIN', 'Fashion Nova', 'Princess Polly', 'Zara', 'H&M']

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">
          Trend Intelligence
        </h1>
        <p className="text-lg text-accent-600">Real-time fashion insights for junior customers (15-28)</p>
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

      {/* Filters */}
      <div className="card p-6 mb-8">
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
                  {plat}
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
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Trends Found</h3>
          <p className="text-accent-600 mb-6">Try adjusting your filters or check back soon for new trends.</p>
          <button
            onClick={() => {
              setCategory('')
              setPlatform('')
              setSortBy('score')
            }}
            className="btn-primary"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  )
}
