import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw, Plus } from 'lucide-react'
import { useTrendById } from '@/hooks/useTrends'
import TrendScoreBadge from '@/components/TrendScoreBadge'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const mockEngagementData = [
  { date: 'Day 1', likes: 2400, comments: 1398, shares: 420 },
  { date: 'Day 2', likes: 3210, comments: 1800, shares: 598 },
  { date: 'Day 3', likes: 4100, comments: 2210, shares: 750 },
  { date: 'Day 4', likes: 5890, comments: 3400, shares: 1220 },
  { date: 'Day 5', likes: 7200, comments: 4100, shares: 1890 },
  { date: 'Day 6', likes: 9100, comments: 5200, shares: 2450 },
  { date: 'Day 7', likes: 11500, comments: 6800, shares: 3100 },
]

export default function TrendDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { trend, loading, error } = useTrendById(id || '')

  if (loading) {
    return (
      <div className="p-6 lg:p-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Trends
        </button>
        <div className="animate-pulse space-y-8">
          <div className="h-96 bg-gradient-to-br from-accent-100 to-accent-50 rounded-lg" />
          <div className="h-32 bg-gradient-to-br from-accent-100 to-accent-50 rounded-lg" />
        </div>
      </div>
    )
  }

  if (error || !trend) {
    return (
      <div className="p-6 lg:p-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Trends
        </button>
        <div className="card p-12 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-display font-bold text-accent-900 mb-2">Trend Not Found</h2>
          <p className="text-accent-600 mb-6">{error || 'This trend could not be loaded.'}</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Return to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header Navigation */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 font-medium"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Trends
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Image */}
          <div className="card overflow-hidden">
            <div className="w-full h-96 bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center">
              {trend.image_url ? (
                <img src={trend.image_url} alt={trend.category} className="w-full h-full object-cover" />
              ) : (
                <div className="text-center">
                  <div className="text-6xl mb-4">👗</div>
                  <p className="text-accent-600">{trend.platform}</p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="card p-4">
              <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Category</p>
              <p className="text-xl font-display font-bold text-accent-900">{trend.category}</p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Platform</p>
              <p className="text-xl font-display font-bold text-accent-900">{trend.platform}</p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Engagement</p>
              <p className="text-xl font-display font-bold text-accent-900">
                {(trend.engagement_count / 1000).toFixed(1)}k
              </p>
            </div>
            <div className="card p-4">
              <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Score</p>
              <TrendScoreBadge score={Math.round(trend.trend_score)} size="md" />
            </div>
          </div>

          {/* Colors */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Colors</h3>
            <div className="flex flex-wrap gap-4">
              {trend.colors.map((color, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full border-2 border-accent-200`} />
                  <span className="font-medium text-accent-700">{color}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Style Tags */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Style Tags</h3>
            <div className="flex flex-wrap gap-3">
              {trend.style_tags.map((tag, idx) => (
                <span key={idx} className="badge-accent">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* AI Analysis */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">AI Analysis</h3>
            <p className="text-accent-700 leading-relaxed">{trend.ai_analysis}</p>
          </div>

          {/* Engagement Chart */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-6">Engagement Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockEngagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FDF2F8',
                    border: '1px solid #F472B6',
                    borderRadius: '8px',
                  }}
                />
                <Line type="monotone" dataKey="likes" stroke="#EC4899" strokeWidth={2} dot={{ fill: '#EC4899' }} />
                <Line type="monotone" dataKey="comments" stroke="#F472B6" strokeWidth={2} dot={{ fill: '#F472B6' }} />
                <Line type="monotone" dataKey="shares" stroke="#DB2777" strokeWidth={2} dot={{ fill: '#DB2777' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Similar Items */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Similar Trends</h3>
            <p className="text-accent-600 mb-6">Related items in the same category coming soon.</p>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Actions */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Actions</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary flex items-center justify-center gap-2">
                <Plus className="w-4 h-4" />
                Add to Mood Board
              </button>
              <button className="w-full btn-secondary flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Re-analyze
              </button>
              <button className="w-full btn-ghost flex items-center justify-center gap-2">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>

          {/* Details */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Details</h3>
            <div className="space-y-4 text-sm">
              <div>
                <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Source URL</p>
                <a
                  href={trend.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700 break-all"
                >
                  Visit Original
                </a>
              </div>
              <div>
                <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Created</p>
                <p className="text-accent-700">{new Date(trend.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Last Updated</p>
                <p className="text-accent-700">{new Date(trend.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Tags */}
          <div className="card p-6">
            <h3 className="font-display font-bold text-accent-900 mb-4">Metrics</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center p-2 bg-accent-50 rounded">
                <span className="text-accent-700">Trend Score</span>
                <span className="font-bold text-primary-600">{Math.round(trend.trend_score)}/100</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-accent-50 rounded">
                <span className="text-accent-700">Engagement</span>
                <span className="font-bold text-primary-600">{(trend.engagement_count / 1000).toFixed(1)}k</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-accent-50 rounded">
                <span className="text-accent-700">Colors</span>
                <span className="font-bold text-primary-600">{trend.colors.length}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-accent-50 rounded">
                <span className="text-accent-700">Tags</span>
                <span className="font-bold text-primary-600">{trend.style_tags.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
