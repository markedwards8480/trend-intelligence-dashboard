import { useState } from 'react'
import { Heart, MessageCircle, Share2, Plus } from 'lucide-react'
import { TrendItem } from '@/types'
import TrendScoreBadge from './TrendScoreBadge'

interface TrendCardProps {
  trend: TrendItem
  onViewDetail?: (id: string) => void
  onAddToMoodBoard?: (trend: TrendItem) => void
}

const formatCount = (num: number): string => {
  if (!num || isNaN(num)) return '0'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`
  return String(num)
}

export default function TrendCard({ trend, onViewDetail, onAddToMoodBoard }: TrendCardProps) {
  const [isLiked, setIsLiked] = useState(false)

  const getColorDot = (color: string) => {
    const colorMap: Record<string, string> = {
      pink: 'bg-pink-400',
      purple: 'bg-purple-400',
      black: 'bg-black',
      white: 'bg-gray-100 border border-gray-300',
      beige: 'bg-amber-100',
      red: 'bg-red-500',
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      yellow: 'bg-yellow-400',
      orange: 'bg-orange-500',
    }
    return colorMap[color.toLowerCase()] || 'bg-gray-300'
  }

  return (
    <div className="card overflow-hidden group cursor-pointer">
      {/* Image Container */}
      <div
        className="relative h-64 bg-gradient-to-br from-primary-100 to-accent-100 overflow-hidden cursor-pointer"
        onClick={() => onViewDetail?.(trend.id)}
      >
        {trend.image_url ? (
          <img
            src={trend.image_url}
            alt={trend.category}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-2">👗</div>
              <p className="text-sm text-accent-500">{trend.platform}</p>
            </div>
          </div>
        )}

        {/* Score Badge - Top Right */}
        <div className="absolute top-3 right-3">
          <TrendScoreBadge score={Math.round(trend.trend_score)} size="sm" />
        </div>

        {/* Category Badge - Top Left */}
        <div className="absolute top-3 left-3">
          <span className="badge-primary text-xs">{trend.category}</span>
        </div>

        {/* Platform Badge - Bottom Left */}
        <div className="absolute bottom-3 left-3">
          <span className="inline-block px-2 py-1 bg-white bg-opacity-90 rounded-full text-xs font-semibold text-accent-900">
            {trend.platform}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Colors */}
        {trend.colors.length > 0 && (
          <div className="flex gap-2 mb-3">
            {trend.colors.slice(0, 5).map((color, idx) => (
              <div
                key={idx}
                className={`w-4 h-4 rounded-full border border-accent-200 ${getColorDot(color)}`}
                title={color}
              />
            ))}
            {trend.colors.length > 5 && (
              <div className="w-4 h-4 flex items-center justify-center text-xs font-bold text-accent-600">
                +{trend.colors.length - 5}
              </div>
            )}
          </div>
        )}

        {/* Style Tags */}
        {trend.style_tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {trend.style_tags.slice(0, 3).map((tag, idx) => (
              <span
                key={idx}
                className="inline-block px-2 py-1 bg-accent-50 text-accent-700 rounded text-xs font-medium hover:bg-accent-100 transition-colors"
              >
                {tag}
              </span>
            ))}
            {trend.style_tags.length > 3 && (
              <span className="text-xs text-accent-500 self-center">
                +{trend.style_tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Engagement Metrics */}
        <div className="flex items-center gap-4 mb-4 text-sm text-accent-600 py-3 border-t border-accent-100">
          <div className="flex items-center gap-1">
            <Heart className="w-4 h-4" />
            <span className="font-medium">{formatCount(trend.likes ?? Math.round((trend.engagement_count || 0) * 0.4))}</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageCircle className="w-4 h-4" />
            <span className="font-medium">{formatCount(trend.comments ?? Math.round((trend.engagement_count || 0) * 0.15))}</span>
          </div>
          <div className="flex items-center gap-1">
            <Share2 className="w-4 h-4" />
            <span className="font-medium">{formatCount(trend.shares ?? Math.round((trend.engagement_count || 0) * 0.08))}</span>
          </div>
        </div>

        {/* Actions */}
        <button
          onClick={() => onAddToMoodBoard?.(trend)}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add to Mood Board
        </button>
      </div>
    </div>
  )
}
