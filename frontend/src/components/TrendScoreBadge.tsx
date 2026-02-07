import { Flame } from 'lucide-react'

interface TrendScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

export default function TrendScoreBadge({ score, size = 'md' }: TrendScoreBadgeProps) {
  let bgColor = 'bg-blue-100'
  let textColor = 'text-blue-700'
  let icon = '❄️'

  if (score >= 80) {
    bgColor = 'bg-red-100'
    textColor = 'text-red-700'
    icon = '🔥'
  } else if (score >= 60) {
    bgColor = 'bg-orange-100'
    textColor = 'text-orange-700'
    icon = '🌶️'
  } else if (score >= 40) {
    bgColor = 'bg-yellow-100'
    textColor = 'text-yellow-700'
    icon = '⭐'
  }

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base',
  }

  return (
    <div className={`${bgColor} ${textColor} ${sizeClasses[size]} rounded-lg font-semibold flex items-center gap-2 w-fit`}>
      <span>{icon}</span>
      <span>{score}</span>
      {size !== 'sm' && (
        <div className="ml-1 w-24 h-2 bg-white rounded-full overflow-hidden">
          <div
            className={`h-full ${
              score >= 80 ? 'bg-red-500' : score >= 60 ? 'bg-orange-500' : score >= 40 ? 'bg-yellow-500' : 'bg-blue-500'
            }`}
            style={{ width: `${score}%` }}
          />
        </div>
      )}
    </div>
  )
}
