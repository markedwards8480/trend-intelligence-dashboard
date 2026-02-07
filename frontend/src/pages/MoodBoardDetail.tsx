import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit2, Download, Trash2 } from 'lucide-react'
import { TrendItem } from '@/types'

const mockItems: TrendItem[] = [
  {
    id: '1',
    url: 'https://instagram.com/p/1',
    platform: 'Instagram',
    category: 'Dresses',
    colors: ['pink', 'white'],
    style_tags: ['Y2K', 'Maxi'],
    trend_score: 92,
    engagement_count: 145000,
    ai_analysis: 'Y2K inspired maxi dress',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    url: 'https://instagram.com/p/2',
    platform: 'Instagram',
    category: 'Tops',
    colors: ['white', 'beige'],
    style_tags: ['Crop Top', 'Minimalist'],
    trend_score: 87,
    engagement_count: 123000,
    ai_analysis: 'Minimalist crop top',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    url: 'https://instagram.com/p/3',
    platform: 'TikTok',
    category: 'Accessories',
    colors: ['gold', 'pink'],
    style_tags: ['Jewelry', 'Statement'],
    trend_score: 78,
    engagement_count: 98000,
    ai_analysis: 'Gold statement jewelry',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    url: 'https://instagram.com/p/4',
    platform: 'SHEIN',
    category: 'Pants',
    colors: ['pink', 'purple'],
    style_tags: ['Cargo', 'Baggy'],
    trend_score: 85,
    engagement_count: 167000,
    ai_analysis: 'Cargo pants in trendy colors',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export default function MoodBoardDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState('Summer Y2K Collection')
  const [description, setDescription] = useState('Nostalgic early 2000s inspired looks perfect for summer')
  const [items] = useState<TrendItem[]>(mockItems)

  const handleSave = () => {
    setIsEditing(false)
  }

  const handleDelete = (itemId: string) => {
    if (confirm('Remove this item from the mood board?')) {
      alert('Item removed!')
    }
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header Navigation */}
      <button
        onClick={() => navigate('/moodboards')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 font-medium"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Mood Boards
      </button>

      {/* Title Section */}
      <div className="card p-8 mb-8">
        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-accent-900 mb-2">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="input-base text-2xl font-display font-bold"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-accent-900 mb-2">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input-base resize-none h-24"
              />
            </div>
            <div className="flex gap-3">
              <button onClick={handleSave} className="btn-primary">
                Save Changes
              </button>
              <button onClick={() => setIsEditing(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-4xl font-display font-bold text-accent-900 mb-2">{title}</h1>
                <p className="text-lg text-accent-600">{description}</p>
              </div>
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 hover:bg-accent-50 rounded-lg transition-colors"
              >
                <Edit2 className="w-5 h-5 text-accent-700" />
              </button>
            </div>
            <div className="flex flex-wrap gap-4 pt-6 border-t border-accent-100">
              <div>
                <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Items</p>
                <p className="text-2xl font-display font-bold text-primary-600">{items.length}</p>
              </div>
              <div>
                <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Created</p>
                <p className="text-lg font-medium text-accent-900">{new Date().toLocaleDateString()}</p>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-8">
        <button className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export as PDF
        </button>
        <button className="btn-ghost text-red-600 hover:bg-red-50 flex items-center gap-2">
          <Trash2 className="w-4 h-4" />
          Delete Board
        </button>
      </div>

      {/* Items Grid - Pinterest Style Masonry */}
      {items.length > 0 ? (
        <div className="columns-1 md:columns-2 lg:columns-4 gap-6 space-y-6">
          {items.map((item) => (
            <div key={item.id} className="card overflow-hidden break-inside-avoid-column group">
              {/* Image */}
              <div className="h-64 bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center group-hover:opacity-75 transition-opacity">
                <div className="text-center">
                  <div className="text-4xl mb-2">👗</div>
                  <p className="text-sm text-accent-500">{item.platform}</p>
                </div>
              </div>

              {/* Content */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-accent-600 font-semibold uppercase mb-1">{item.category}</p>
                    <h3 className="font-display font-bold text-accent-900">Trend Item</h3>
                  </div>
                  <div className="px-2 py-1 bg-primary-100 rounded text-primary-700 font-semibold text-sm">
                    {Math.round(item.trend_score)}
                  </div>
                </div>

                {/* Colors */}
                <div className="flex gap-2 mb-3">
                  {item.colors.slice(0, 3).map((color, idx) => (
                    <div
                      key={idx}
                      className="w-4 h-4 rounded-full border border-accent-200 bg-gray-300"
                      title={color}
                    />
                  ))}
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {item.style_tags.slice(0, 2).map((tag, idx) => (
                    <span key={idx} className="text-xs px-2 py-1 bg-accent-50 text-accent-700 rounded">
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => handleDelete(item.id)}
                  className="w-full btn-ghost text-red-600 hover:bg-red-50 py-2"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-16 text-center">
          <div className="text-5xl mb-4">📦</div>
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Items Yet</h3>
          <p className="text-accent-600 mb-6">Start adding trends to your mood board.</p>
          <button onClick={() => navigate('/submit')} className="btn-primary">
            Browse Trends
          </button>
        </div>
      )}
    </div>
  )
}
