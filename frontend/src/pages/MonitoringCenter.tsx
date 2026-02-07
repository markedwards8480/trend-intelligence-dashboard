import { useState } from 'react'
import { Plus, Trash2, AlertCircle } from 'lucide-react'
import { MonitoringTarget } from '@/types'

interface MonitoringTargetWithUI extends MonitoringTarget {
  status: 'active' | 'inactive'
}

const mockTargets: MonitoringTargetWithUI[] = [
  {
    id: '1',
    platform: 'Instagram',
    search_term: 'Y2K Fashion',
    is_active: true,
    status: 'active',
    last_checked: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    created_at: '2024-01-01',
  },
  {
    id: '2',
    platform: 'TikTok',
    search_term: '#MiniSkirtChallenge',
    is_active: true,
    status: 'active',
    last_checked: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    created_at: '2024-01-02',
  },
  {
    id: '3',
    platform: 'SHEIN',
    search_term: 'Cargo Pants',
    is_active: false,
    status: 'inactive',
    last_checked: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    created_at: '2024-01-03',
  },
  {
    id: '4',
    platform: 'Instagram',
    search_term: '@fashioninfluencer',
    is_active: true,
    status: 'active',
    last_checked: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    created_at: '2024-01-04',
  },
  {
    id: '5',
    platform: 'Fashion Nova',
    search_term: 'Bodysuit Trends',
    is_active: true,
    status: 'active',
    last_checked: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    created_at: '2024-01-05',
  },
]

export default function MonitoringCenter() {
  const [targets, setTargets] = useState<MonitoringTargetWithUI[]>(mockTargets)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newPlatform, setNewPlatform] = useState('Instagram')
  const [newSearchTerm, setNewSearchTerm] = useState('')

  const platforms = ['Instagram', 'TikTok', 'SHEIN', 'Fashion Nova', 'Princess Polly', 'Zara', 'H&M']

  const handleAddTarget = () => {
    if (newSearchTerm.trim()) {
      const newTarget: MonitoringTargetWithUI = {
        id: Date.now().toString(),
        platform: newPlatform,
        search_term: newSearchTerm,
        is_active: true,
        status: 'active',
        last_checked: new Date().toISOString(),
        created_at: new Date().toISOString().split('T')[0],
      }
      setTargets([newTarget, ...targets])
      setNewSearchTerm('')
      setShowAddForm(false)
    }
  }

  const toggleTarget = (id: string) => {
    setTargets(
      targets.map((t) =>
        t.id === id ? { ...t, is_active: !t.is_active, status: t.is_active ? 'inactive' : 'active' } : t
      )
    )
  }

  const deleteTarget = (id: string) => {
    if (confirm('Remove this monitoring target?')) {
      setTargets(targets.filter((t) => t.id !== id))
    }
  }

  const groupedTargets = platforms.reduce(
    (acc, platform) => {
      acc[platform] = targets.filter((t) => t.platform === platform)
      return acc
    },
    {} as Record<string, MonitoringTargetWithUI[]>
  )

  const getLastCheckedText = (date: string) => {
    const ms = Date.now() - new Date(date).getTime()
    const mins = Math.floor(ms / 1000 / 60)
    const hours = Math.floor(mins / 60)

    if (mins < 1) return 'Just now'
    if (mins < 60) return `${mins}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
        <div>
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">Monitoring Center</h1>
          <p className="text-lg text-accent-600">Track trends across platforms in real-time</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary mt-6 lg:mt-0 flex items-center justify-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Target
        </button>
      </div>

      {/* Add Target Form */}
      {showAddForm && (
        <div className="card p-6 mb-8">
          <h3 className="font-display font-bold text-accent-900 mb-6">Add Monitoring Target</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-accent-900 mb-2">Platform</label>
              <select
                value={newPlatform}
                onChange={(e) => setNewPlatform(e.target.value)}
                className="input-base"
              >
                {platforms.map((plat) => (
                  <option key={plat} value={plat}>
                    {plat}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-accent-900 mb-2">Search Term / Hashtag / Handle</label>
              <input
                type="text"
                value={newSearchTerm}
                onChange={(e) => setNewSearchTerm(e.target.value)}
                placeholder="e.g., #Y2K, @fashioninfluencer, Cargo Pants"
                className="input-base"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={handleAddTarget} className="btn-primary">
              Add Target
            </button>
            <button onClick={() => setShowAddForm(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Active Targets Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card p-4">
          <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Total Targets</p>
          <p className="text-2xl font-display font-bold text-accent-900">{targets.length}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Active</p>
          <p className="text-2xl font-display font-bold text-green-600">{targets.filter((t) => t.is_active).length}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Inactive</p>
          <p className="text-2xl font-display font-bold text-orange-600">{targets.filter((t) => !t.is_active).length}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-accent-600 font-semibold uppercase mb-1">Check Frequency</p>
          <p className="text-2xl font-display font-bold text-primary-600">5min</p>
        </div>
      </div>

      {/* Monitoring Targets by Platform */}
      <div className="space-y-8">
        {Object.entries(groupedTargets).map(([platform, platformTargets]) => {
          if (platformTargets.length === 0) return null

          return (
            <div key={platform}>
              <h2 className="text-xl font-display font-bold text-accent-900 mb-4">{platform}</h2>
              <div className="space-y-3">
                {platformTargets.map((target) => (
                  <div key={target.id} className="card p-6 flex items-center justify-between hover:shadow-md transition-shadow">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h3 className="font-display font-bold text-accent-900 text-lg">{target.search_term}</h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            target.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-orange-100 text-orange-700'
                          }`}
                        >
                          {target.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-accent-600">
                        <AlertCircle className="w-4 h-4" />
                        <span>Last checked: {getLastCheckedText(target.last_checked)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {/* Toggle Switch */}
                      <button
                        onClick={() => toggleTarget(target.id)}
                        className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                          target.is_active ? 'bg-green-500' : 'bg-accent-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                            target.is_active ? 'translate-x-7' : 'translate-x-1'
                          }`}
                        />
                      </button>

                      {/* Delete Button */}
                      <button
                        onClick={() => deleteTarget(target.id)}
                        className="p-2 hover:bg-red-50 rounded-lg transition-colors text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {targets.length === 0 && (
        <div className="card p-16 text-center">
          <div className="text-5xl mb-4">📡</div>
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No Monitoring Targets</h3>
          <p className="text-accent-600 mb-6">Create your first monitoring target to track trends automatically.</p>
          <button onClick={() => setShowAddForm(true)} className="btn-primary mx-auto">
            Add Target
          </button>
        </div>
      )}
    </div>
  )
}
