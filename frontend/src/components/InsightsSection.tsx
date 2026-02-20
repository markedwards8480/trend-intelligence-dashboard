import { useState, useEffect, useCallback } from 'react'
import { Sparkles, RefreshCw, TrendingUp, Palette, Tag, ChevronRight, Users } from 'lucide-react'
import { TrendInsight, ThemedLook, InsightsData, DEMOGRAPHIC_SHORT_LABELS, Demographic } from '@/types'
import { startInsightsGeneration, getInsightsStatus, getInsights } from '@/api/insights'

interface InsightsSectionProps {
  demographic?: string
  onFilterByCategory?: (category: string) => void
  onFilterByStyleTags?: (tags: string[]) => void
}

// Color name → CSS color mapping for palette swatches
const COLOR_CSS: Record<string, string> = {
  black: '#1a1a1a', white: '#f5f5f5', cream: '#FFFDD0', ivory: '#FFFFF0',
  navy: '#001f3f', 'navy blue': '#001f3f', blue: '#3B82F6', 'powder blue': '#B0E0E6',
  red: '#EF4444', burgundy: '#800020', rust: '#B7410E', 'burnt orange': '#CC5500',
  pink: '#EC4899', 'blush pink': '#FFB6C1', 'dusty rose': '#DCAE96', mauve: '#E0B0FF',
  'rose gold': '#B76E79',
  green: '#22C55E', 'sage green': '#B2AC88', 'olive green': '#556B2F', 'forest green': '#228B22',
  yellow: '#EAB308', 'butter yellow': '#FFFD74', gold: '#FFD700',
  brown: '#92400E', 'chocolate brown': '#3B1E08', camel: '#C19A6B', tan: '#D2B48C', taupe: '#483C32',
  grey: '#6B7280', gray: '#6B7280', 'charcoal grey': '#36454F', charcoal: '#36454F', silver: '#C0C0C0',
  purple: '#8B5CF6', lavender: '#E6E6FA', lilac: '#C8A2C8',
  orange: '#F97316', coral: '#FF6F61', peach: '#FFDAB9',
  denim: '#1560BD', khaki: '#C3B091', beige: '#F5F5DC',
}

function getColorCSS(name: string): string {
  const lower = name.toLowerCase().trim()
  return COLOR_CSS[lower] || '#CBD5E1'
}

function ColorDot({ color }: { color: string }) {
  const bg = getColorCSS(color)
  const isBright = ['white', 'cream', 'ivory', 'butter yellow'].includes(color.toLowerCase())
  return (
    <span
      title={color}
      className={`inline-block w-4 h-4 rounded-full shrink-0 ${isBright ? 'border border-accent-300' : ''}`}
      style={{ backgroundColor: bg }}
    />
  )
}

export default function InsightsSection({ demographic, onFilterByCategory, onFilterByStyleTags }: InsightsSectionProps) {
  const [data, setData] = useState<InsightsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState<string | null>(null)

  const fetchInsights = useCallback(async () => {
    try {
      const result = await getInsights(demographic || undefined)
      setData(result)
    } catch {
      // silently fail
    } finally {
      setLoading(false)
    }
  }, [demographic])

  useEffect(() => {
    fetchInsights()
  }, [fetchInsights])

  const handleGenerate = async () => {
    setGenerating(true)
    setProgress('Starting...')
    try {
      await startInsightsGeneration()

      // Poll for status
      const poll = setInterval(async () => {
        try {
          const status = await getInsightsStatus()
          setProgress(status.progress || status.status)

          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(poll)
            setGenerating(false)
            if (status.status === 'completed') {
              await fetchInsights()
            }
            setProgress(null)
          }
        } catch {
          clearInterval(poll)
          setGenerating(false)
          setProgress(null)
        }
      }, 3000)
    } catch {
      setGenerating(false)
      setProgress(null)
    }
  }

  const hasInsights = data && (data.category_insights.length > 0 || data.themed_looks.length > 0)

  if (loading) {
    return (
      <div className="space-y-4 mb-8">
        <div className="card h-32 bg-gradient-to-br from-accent-50 to-accent-100 animate-pulse" />
      </div>
    )
  }

  // No insights yet — show generate prompt
  if (!hasInsights) {
    return (
      <div className="card p-6 mb-8 border-dashed border-2 border-primary-200 bg-gradient-to-br from-primary-50/30 to-accent-50/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-xl">
              <Sparkles className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <h3 className="font-display font-bold text-accent-900">Trend Intelligence Insights</h3>
              <p className="text-sm text-accent-500">
                AI-generated category summaries and themed fashion looks based on your trend data
              </p>
            </div>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="btn-primary text-sm px-5 py-2.5"
          >
            {generating ? (
              <span className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                {progress || 'Generating...'}
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Generate Insights
              </span>
            )}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 mb-10">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-100 rounded-xl">
            <Sparkles className="w-6 h-6 text-primary-500" />
          </div>
          <div>
            <h2 className="text-2xl font-display font-bold text-accent-900">Trend Intelligence</h2>
            <p className="text-sm text-accent-500">
              AI-powered insights from {data!.category_insights.reduce((s, i) => s + i.trending_items_count, 0)} trends
              {data!.generated_at && ` · Updated ${new Date(data!.generated_at).toLocaleDateString()}`}
            </p>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1.5 font-medium"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          {generating ? (progress || 'Generating...') : 'Regenerate'}
        </button>
      </div>

      {/* Category Insights */}
      {data!.category_insights.length > 0 && (
        <div>
          <h3 className="text-lg font-display font-bold text-accent-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-500" />
            What's Trending
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data!.category_insights.map((insight) => (
              <CategoryCard
                key={insight.id}
                insight={insight}
                onClick={() => onFilterByCategory?.(insight.category)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Themed Looks */}
      {data!.themed_looks.length > 0 && (
        <div>
          <h3 className="text-lg font-display font-bold text-accent-800 mb-4 flex items-center gap-2">
            <Palette className="w-5 h-5 text-primary-500" />
            Trending Themes
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {data!.themed_looks.map((theme) => (
              <ThemeCard
                key={theme.id}
                theme={theme}
                onExplore={() => onFilterByStyleTags?.(theme.style_tags)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


function CategoryCard({ insight, onClick }: { insight: TrendInsight; onClick?: () => void }) {
  const chars = insight.key_characteristics || {}
  const colors = chars.dominant_colors || []
  const styles = chars.dominant_styles || []

  return (
    <div
      onClick={onClick}
      className="card p-5 cursor-pointer hover:border-primary-200 hover:shadow-md transition-all group"
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-display font-bold text-accent-900 capitalize text-base">{insight.category}</h4>
        <div className="flex items-center gap-1.5 text-xs text-accent-500">
          <span className="font-bold text-primary-600">{insight.trending_items_count}</span>
          <span>items</span>
          <ChevronRight className="w-3.5 h-3.5 text-accent-400 group-hover:text-primary-500 transition-colors" />
        </div>
      </div>

      <p className="text-sm text-accent-600 leading-relaxed mb-3">{insight.summary}</p>

      {/* Color dots */}
      {colors.length > 0 && (
        <div className="flex items-center gap-1.5 mb-2">
          {colors.slice(0, 6).map((c, i) => (
            <ColorDot key={i} color={c} />
          ))}
        </div>
      )}

      {/* Style tags */}
      {styles.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {styles.slice(0, 4).map((s, i) => (
            <span
              key={i}
              className="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full font-medium"
            >
              {s}
            </span>
          ))}
        </div>
      )}

      {/* Score bar */}
      <div className="mt-3 flex items-center gap-2">
        <div className="flex-1 bg-accent-100 rounded-full h-1.5">
          <div
            className="bg-gradient-to-r from-primary-400 to-primary-600 h-1.5 rounded-full"
            style={{ width: `${Math.min(100, (insight.avg_trend_score / 100) * 100)}%` }}
          />
        </div>
        <span className="text-xs font-bold text-accent-500">{insight.avg_trend_score.toFixed(0)}</span>
      </div>
    </div>
  )
}


function ThemeCard({ theme, onExplore }: { theme: ThemedLook; onExplore?: () => void }) {
  return (
    <div className="card overflow-hidden hover:shadow-lg transition-all">
      {/* Color palette header */}
      <div className="flex h-3">
        {theme.color_palette.map((color, i) => (
          <div
            key={i}
            className="flex-1"
            style={{ backgroundColor: getColorCSS(color) }}
          />
        ))}
      </div>

      <div className="p-5">
        {/* Theme name + mood */}
        <h4 className="font-display font-bold text-xl text-accent-900 mb-1">{theme.theme_name}</h4>
        {theme.mood_description && (
          <p className="text-sm text-primary-600 italic mb-3">{theme.mood_description}</p>
        )}

        <p className="text-sm text-accent-600 leading-relaxed mb-4">{theme.description}</p>

        {/* Key items */}
        <div className="space-y-1.5 mb-4">
          {theme.key_items.slice(0, 4).map((item, i) => (
            <div key={i} className="flex items-center gap-2 text-sm">
              <span className="text-primary-400">•</span>
              <span className="text-accent-700 capitalize font-medium">{item.category}</span>
              <span className="text-accent-400">—</span>
              <span className="text-accent-500 truncate">{item.description}</span>
            </div>
          ))}
        </div>

        {/* Color palette swatches with labels */}
        <div className="flex items-center gap-2 mb-3">
          <Palette className="w-3.5 h-3.5 text-accent-400" />
          <div className="flex items-center gap-1.5">
            {theme.color_palette.map((color, i) => (
              <div key={i} className="flex items-center gap-1">
                <ColorDot color={color} />
                <span className="text-xs text-accent-500 capitalize">{color}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Style tags */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {theme.style_tags.map((tag, i) => (
            <span key={i} className="text-xs px-2 py-0.5 bg-accent-50 text-accent-700 rounded-full">
              {tag}
            </span>
          ))}
        </div>

        {/* Demographics + Explore */}
        <div className="flex items-center justify-between pt-3 border-t border-accent-100">
          <div className="flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-accent-400" />
            {theme.demographic_appeal.map((d, i) => (
              <span key={i} className="text-xs text-accent-500">
                {DEMOGRAPHIC_SHORT_LABELS[d as Demographic] || d}
                {i < theme.demographic_appeal.length - 1 ? ',' : ''}
              </span>
            ))}
          </div>
          <button
            onClick={onExplore}
            className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            Explore
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
