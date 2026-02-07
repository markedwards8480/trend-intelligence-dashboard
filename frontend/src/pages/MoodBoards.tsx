import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Calendar, Image } from 'lucide-react'

interface MoodBoard {
  id: string
  title: string
  description: string
  itemCount: number
  createdAt: string
  thumbnail?: string
}

const mockMoodBoards: MoodBoard[] = [
  {
    id: '1',
    title: 'Summer Y2K Collection',
    description: 'Nostalgic early 2000s inspired looks perfect for summer',
    itemCount: 12,
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    title: 'Minimalist Essentials',
    description: 'Clean, simple pieces for everyday wear',
    itemCount: 8,
    createdAt: '2024-01-10',
  },
  {
    id: '3',
    title: 'Bold Statement Pieces',
    description: 'Eye-catching items that make an impact',
    itemCount: 15,
    createdAt: '2024-01-05',
  },
  {
    id: '4',
    title: 'Streetwear Inspo',
    description: 'Urban and edgy fashion inspirations',
    itemCount: 20,
    createdAt: '2023-12-28',
  },
]

export default function MoodBoards() {
  const navigate = useNavigate()
  const [moodBoards, setMoodBoards] = useState<MoodBoard[]>(mockMoodBoards)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newBoardTitle, setNewBoardTitle] = useState('')
  const [newBoardDescription, setNewBoardDescription] = useState('')

  const handleCreateBoard = () => {
    if (newBoardTitle.trim()) {
      const newBoard: MoodBoard = {
        id: Date.now().toString(),
        title: newBoardTitle,
        description: newBoardDescription,
        itemCount: 0,
        createdAt: new Date().toISOString().split('T')[0],
      }
      setMoodBoards([newBoard, ...moodBoards])
      setNewBoardTitle('')
      setNewBoardDescription('')
      setShowCreateModal(false)
    }
  }

  const handleDeleteBoard = (id: string) => {
    if (confirm('Are you sure you want to delete this mood board?')) {
      setMoodBoards(moodBoards.filter((b) => b.id !== id))
    }
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-12">
        <div>
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">Mood Boards</h1>
          <p className="text-lg text-accent-600">Curate and organize trends into thematic collections</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary mt-6 lg:mt-0 flex items-center justify-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Mood Board
        </button>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-md p-8">
            <h2 className="text-2xl font-display font-bold text-accent-900 mb-6">Create Mood Board</h2>

            <div className="space-y-4 mb-8">
              <div>
                <label className="block text-sm font-semibold text-accent-900 mb-2">Title</label>
                <input
                  type="text"
                  value={newBoardTitle}
                  onChange={(e) => setNewBoardTitle(e.target.value)}
                  placeholder="e.g., Summer Y2K Vibes"
                  className="input-base"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-accent-900 mb-2">Description</label>
                <textarea
                  value={newBoardDescription}
                  onChange={(e) => setNewBoardDescription(e.target.value)}
                  placeholder="Describe the mood and aesthetic..."
                  className="input-base resize-none h-24"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewBoardTitle('')
                  setNewBoardDescription('')
                }}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button onClick={handleCreateBoard} className="flex-1 btn-primary">
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mood Boards Grid */}
      {moodBoards.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {moodBoards.map((board) => (
            <div
              key={board.id}
              className="card overflow-hidden group cursor-pointer"
              onClick={() => navigate(`/moodboards/${board.id}`)}
            >
              {/* Thumbnail */}
              <div className="h-48 bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center group-hover:from-primary-200 group-hover:to-accent-200 transition-colors">
                <Image className="w-12 h-12 text-primary-600" />
              </div>

              {/* Content */}
              <div className="p-4">
                <h3 className="font-display font-bold text-accent-900 mb-2 line-clamp-2">{board.title}</h3>
                <p className="text-sm text-accent-600 mb-4 line-clamp-2">{board.description}</p>

                <div className="flex items-center justify-between pt-4 border-t border-accent-100 text-xs text-accent-600">
                  <div className="flex items-center gap-1">
                    <Image className="w-4 h-4" />
                    <span>{board.itemCount} items</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(board.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteBoard(board.id)
                  }}
                  className="w-full mt-4 btn-ghost text-red-600 hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-16 text-center">
          <div className="text-5xl mb-4">🎨</div>
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Mood Boards Yet</h3>
          <p className="text-accent-600 mb-6">Create your first mood board to start curating trends.</p>
          <button onClick={() => setShowCreateModal(true)} className="btn-primary mx-auto">
            Create Mood Board
          </button>
        </div>
      )}
    </div>
  )
}
