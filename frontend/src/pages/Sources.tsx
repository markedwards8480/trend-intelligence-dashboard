import { useState } from 'react'
import { Globe, Plus, Trash2, ExternalLink, Sparkles, ChevronDown, ChevronUp, Power, Search, Upload, Instagram, Zap } from 'lucide-react'
import { useSources, useSourceSuggestions } from '@/hooks/useSources'
import { DEMOGRAPHICS, DEMOGRAPHIC_LABELS, Demographic, SourceCreate, SourceSuggestion } from '@/types'
import { analyzeFromSource } from '@/api/sources'
import { seedTrendsFromSources } from '@/api/trends'
import ExcelImportModal from '@/components/ExcelImportModal'
import SocialDiscoveryModal from '@/components/SocialDiscoveryModal'

// Source categories — user picks the type, brand name comes from the Source Name field
const SOURCE_CATEGORIES = [
  { value: 'ecommerce', label: 'Ecommerce Site' },
  { value: 'social', label: 'Social Media' },
  { value: 'media', label: 'Fashion Media / Magazine' },
  { value: 'search', label: 'Search & Trends' },
  { value: 'other', label: 'Other' },
]

const CATEGORY_LABELS: Record<string, string> = {
  ecommerce: 'Ecommerce',
  social: 'Social Media',
  media: 'Fashion Media',
  search: 'Search & Trends',
  other: 'Other',
}

export default function Sources() {
  const { sources, loading, addSource, removeSource, toggleSource, refetch } = useSources()
  const { suggestions, loading: suggestionsLoading, fetchSuggestions } = useSourceSuggestions()

  // Add source form state
  const [showAddForm, setShowAddForm] = useState(false)
  const [formUrl, setFormUrl] = useState('')
  const [formPlatform, setFormPlatform] = useState('ecommerce')
  const [formName, setFormName] = useState('')
  const [formDemographics, setFormDemographics] = useState<string[]>(['junior_girls'])
  const [formFrequency, setFormFrequency] = useState('manual')
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Analyze from source state
  const [analyzeSourceId, setAnalyzeSourceId] = useState<number | null>(null)
  const [analyzeUrl, setAnalyzeUrl] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeResult, setAnalyzeResult] = useState<string | null>(null)

  // Import modal
  const [showImportModal, setShowImportModal] = useState(false)

  // Social discovery modal
  const [showSocialDiscovery, setShowSocialDiscovery] = useState(false)

  // Seed trends state
  const [seeding, setSeeding] = useState(false)
  const [seedResult, setSeedResult] = useState<{ created: number; skipped: number; errors: number } | null>(null)
  const [seedError, setSeedError] = useState('')

  const handleSeedTrends = async () => {
    if (!confirm('Generate ~200 AI trend items from your ecommerce brands? This may take 2-3 minutes.')) return
    setSeeding(true)
    setSeedError('')
    setSeedResult(null)
    try {
      const result = await seedTrendsFromSources()
      setSeedResult(result)
    } catch (err: any) {
      setSeedError(err.response?.data?.detail || err.message || 'Seed generation failed')
    } finally {
      setSeeding(false)
    }
  }

  // Suggestions visibility
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    if (!formUrl || !formName) {
      setFormError('Please fill in all required fields')
      return
    }
    setSubmitting(true)
    try {
      await addSource({
        url: formUrl,
        platform: formPlatform,
        name: formName,
        target_demographics: formDemographics,
        frequency: formFrequency,
      })
      setFormUrl('')
      setFormName('')
      setFormDemographics(['junior_girls'])
      setShowAddForm(false)
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || 'Failed to add source')
    } finally {
      setSubmitting(false)
    }
  }

  // Map AI suggestion platform names to our category values
  const platformToCategory = (platform: string): string => {
    const p = platform.toLowerCase()
    if (['instagram', 'tiktok', 'pinterest', 'youtube'].some(s => p.includes(s))) return 'social'
    if (['vogue', 'elle', 'wwd', 'harper', 'refinery', 'glamour', 'instyle', 'cosmo', 'who what wear', 'zoe report'].some(s => p.includes(s))) return 'media'
    if (['google trends', 'google shopping'].some(s => p.includes(s))) return 'search'
    // Default most fashion sites to ecommerce
    return 'ecommerce'
  }

  const handleAddSuggestion = async (suggestion: SourceSuggestion) => {
    try {
      await addSource({
        url: suggestion.url,
        platform: platformToCategory(suggestion.platform),
        name: suggestion.name,
        target_demographics: suggestion.demographics,
        frequency: 'manual',
      })
    } catch {
      // May already exist
    }
  }

  const handleAnalyze = async (sourceId: number) => {
    if (!analyzeUrl) return
    setAnalyzing(true)
    setAnalyzeResult(null)
    try {
      const result = await analyzeFromSource(sourceId, analyzeUrl)
      setAnalyzeResult(`Analyzed: ${result.category} — Score: ${Math.round(result.trend_score)}`)
      setAnalyzeUrl('')
      setAnalyzeSourceId(null)
      refetch()
    } catch (err: any) {
      setAnalyzeResult(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const toggleDemographic = (demo: string) => {
    setFormDemographics((prev) =>
      prev.includes(demo) ? prev.filter((d) => d !== demo) : [...prev, demo]
    )
  }

  // Group sources by their platform (which is now a category value)
  const ecommerceSources = sources.filter((s) => s.platform === 'ecommerce')
  const socialSources = sources.filter((s) => s.platform === 'social')
  const mediaSources = sources.filter((s) => s.platform === 'media')
  const searchSources = sources.filter((s) => s.platform === 'search')
  const otherSources = sources.filter((s) =>
    !['ecommerce', 'social', 'media', 'search'].includes(s.platform)
  )

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">
            Trend Sources
          </h1>
          <p className="text-lg text-accent-600">
            Manage the sites and accounts you monitor for fashion trends
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSeedTrends}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 transition-all shadow-sm disabled:opacity-50"
          >
            <Zap className="w-5 h-5" />
            {seeding ? 'Generating...' : 'Populate Trends'}
          </button>
          <button
            onClick={() => setShowSocialDiscovery(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all shadow-sm"
          >
            <Instagram className="w-5 h-5" />
            Discover Social
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            className="btn-secondary flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Import Excel
          </button>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Source
          </button>
        </div>
      </div>

      {/* Analysis result toast */}
      {analyzeResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800 flex items-center justify-between">
          <span>{analyzeResult}</span>
          <button onClick={() => setAnalyzeResult(null)} className="text-green-600 hover:text-green-800">×</button>
        </div>
      )}

      {/* Add Source Form */}
      {showAddForm && (
        <div className="card p-6 mb-8">
          <h3 className="text-lg font-display font-bold text-accent-900 mb-4">Add New Source</h3>
          <form onSubmit={handleAddSource} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-accent-900 mb-1">Source Name *</label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g., SHEIN US, Zara New Arrivals"
                  className="input-base"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-accent-900 mb-1">URL *</label>
                <input
                  type="url"
                  value={formUrl}
                  onChange={(e) => setFormUrl(e.target.value)}
                  placeholder="https://www.shein.com"
                  className="input-base"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-accent-900 mb-1">Category</label>
                <select
                  value={formPlatform}
                  onChange={(e) => setFormPlatform(e.target.value)}
                  className="input-base"
                >
                  {SOURCE_CATEGORIES.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-accent-900 mb-2">Target Demographics</label>
                <div className="flex flex-wrap gap-2">
                  {DEMOGRAPHICS.map((demo) => (
                    <button
                      key={demo}
                      type="button"
                      onClick={() => toggleDemographic(demo)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                        formDemographics.includes(demo)
                          ? 'bg-primary-100 border-primary-300 text-primary-700'
                          : 'bg-white border-accent-200 text-accent-600 hover:border-accent-300'
                      }`}
                    >
                      {DEMOGRAPHIC_LABELS[demo as Demographic]}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-accent-900 mb-1">Check Frequency</label>
                <select
                  value={formFrequency}
                  onChange={(e) => setFormFrequency(e.target.value)}
                  className="input-base"
                >
                  <option value="manual">Manual</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
            </div>

            {formError && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">{formError}</div>
            )}

            <div className="flex gap-3">
              <button type="submit" disabled={submitting} className="btn-primary">
                {submitting ? 'Adding...' : 'Add Source'}
              </button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Seed Generation Status */}
      {seeding && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800">
          <div className="flex items-center gap-3">
            <div className="animate-spin w-5 h-5 border-2 border-amber-500 border-t-transparent rounded-full" />
            <div>
              <p className="font-medium">Generating trend data from your ecommerce brands...</p>
              <p className="text-sm">AI is analyzing 40 brands and creating ~200 trending products. This takes 2-3 minutes.</p>
            </div>
          </div>
        </div>
      )}
      {seedResult && (
        <div className="mb-6 p-4 rounded-xl bg-green-50 border border-green-200 text-green-800">
          <p className="font-medium">
            {seedResult.created} trends created from {sources.filter(s => s.platform === 'ecommerce').length} brands!
            {seedResult.skipped > 0 && ` (${seedResult.skipped} duplicates skipped)`}
          </p>
          <a href="/" className="text-sm underline hover:text-green-900">View Dashboard →</a>
        </div>
      )}
      {seedError && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800">
          <p className="font-medium">Seed generation failed: {seedError}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-accent-900">{sources.length}</p>
          <p className="text-sm text-accent-600">Total Sources</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-accent-900">{ecommerceSources.length}</p>
          <p className="text-sm text-accent-600">Ecommerce</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-accent-900">{socialSources.length}</p>
          <p className="text-sm text-accent-600">Social Media</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-accent-900">{mediaSources.length}</p>
          <p className="text-sm text-accent-600">Fashion Media</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-accent-900">{searchSources.length}</p>
          <p className="text-sm text-accent-600">Search / Trends</p>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
          <p className="text-accent-600">Loading sources...</p>
        </div>
      )}

      {/* Sources Lists */}
      {!loading && sources.length === 0 && (
        <div className="card p-16 text-center mb-8">
          <Globe className="w-12 h-12 text-accent-300 mx-auto mb-4" />
          <h3 className="text-xl font-display font-bold text-accent-900 mb-2">No Sources Yet</h3>
          <p className="text-accent-600 mb-6">
            Add ecommerce sites and social media accounts to start tracking fashion trends.
          </p>
          <button onClick={() => setShowAddForm(true)} className="btn-primary">
            <Plus className="w-4 h-4 inline mr-2" />
            Add Your First Source
          </button>
        </div>
      )}

      {ecommerceSources.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-accent-900 mb-4">Ecommerce Sites</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ecommerceSources.map((source) => (
              <SourceCard
                key={source.id}
                source={source}
                onToggle={() => toggleSource(source.id, !source.active)}
                onDelete={() => removeSource(source.id)}
                onAnalyze={() => setAnalyzeSourceId(analyzeSourceId === source.id ? null : source.id)}
                showAnalyze={analyzeSourceId === source.id}
                analyzeUrl={analyzeUrl}
                onAnalyzeUrlChange={setAnalyzeUrl}
                onSubmitAnalyze={() => handleAnalyze(source.id)}
                analyzing={analyzing}
              />
            ))}
          </div>
        </div>
      )}

      {socialSources.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-accent-900 mb-4">Social Media Accounts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {socialSources.map((source) => (
              <SourceCard
                key={source.id}
                source={source}
                onToggle={() => toggleSource(source.id, !source.active)}
                onDelete={() => removeSource(source.id)}
                onAnalyze={() => setAnalyzeSourceId(analyzeSourceId === source.id ? null : source.id)}
                showAnalyze={analyzeSourceId === source.id}
                analyzeUrl={analyzeUrl}
                onAnalyzeUrlChange={setAnalyzeUrl}
                onSubmitAnalyze={() => handleAnalyze(source.id)}
                analyzing={analyzing}
              />
            ))}
          </div>
        </div>
      )}

      {mediaSources.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-accent-900 mb-4">Fashion Media & Magazines</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mediaSources.map((source) => (
              <SourceCard
                key={source.id}
                source={source}
                onToggle={() => toggleSource(source.id, !source.active)}
                onDelete={() => removeSource(source.id)}
                onAnalyze={() => setAnalyzeSourceId(analyzeSourceId === source.id ? null : source.id)}
                showAnalyze={analyzeSourceId === source.id}
                analyzeUrl={analyzeUrl}
                onAnalyzeUrlChange={setAnalyzeUrl}
                onSubmitAnalyze={() => handleAnalyze(source.id)}
                analyzing={analyzing}
              />
            ))}
          </div>
        </div>
      )}

      {searchSources.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-accent-900 mb-4">Search & Trend Data</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {searchSources.map((source) => (
              <SourceCard
                key={source.id}
                source={source}
                onToggle={() => toggleSource(source.id, !source.active)}
                onDelete={() => removeSource(source.id)}
                onAnalyze={() => setAnalyzeSourceId(analyzeSourceId === source.id ? null : source.id)}
                showAnalyze={analyzeSourceId === source.id}
                analyzeUrl={analyzeUrl}
                onAnalyzeUrlChange={setAnalyzeUrl}
                onSubmitAnalyze={() => handleAnalyze(source.id)}
                analyzing={analyzing}
              />
            ))}
          </div>
        </div>
      )}

      {otherSources.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-accent-900 mb-4">Other Sources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {otherSources.map((source) => (
              <SourceCard
                key={source.id}
                source={source}
                onToggle={() => toggleSource(source.id, !source.active)}
                onDelete={() => removeSource(source.id)}
                onAnalyze={() => setAnalyzeSourceId(analyzeSourceId === source.id ? null : source.id)}
                showAnalyze={analyzeSourceId === source.id}
                analyzeUrl={analyzeUrl}
                onAnalyzeUrlChange={setAnalyzeUrl}
                onSubmitAnalyze={() => handleAnalyze(source.id)}
                analyzing={analyzing}
              />
            ))}
          </div>
        </div>
      )}

      {/* AI Suggestions */}
      <div className="card p-6">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => {
            setShowSuggestions(!showSuggestions)
            if (!showSuggestions && suggestions.length === 0) fetchSuggestions()
          }}
        >
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-display font-bold text-accent-900">Discover New Sources</h2>
          </div>
          {showSuggestions ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>

        {showSuggestions && (
          <div className="mt-4">
            <p className="text-sm text-accent-600 mb-4">
              AI-powered suggestions based on your current sources and target demographics.
            </p>

            {suggestionsLoading && (
              <div className="flex items-center gap-2 text-accent-600">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600" />
                <span>Analyzing your sources and finding recommendations...</span>
              </div>
            )}

            {!suggestionsLoading && suggestions.length > 0 && (
              <div className="space-y-3">
                {suggestions.map((s, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 bg-accent-50 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-accent-900">{s.name}</span>
                        <span className="text-xs px-2 py-0.5 bg-accent-200 rounded-full text-accent-700">{s.platform}</span>
                      </div>
                      <p className="text-sm text-accent-600 mb-1">{s.reasoning}</p>
                      <div className="flex gap-1">
                        {s.demographics.map((d) => (
                          <span key={d} className="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">
                            {DEMOGRAPHIC_LABELS[d as Demographic] || d}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => handleAddSuggestion(s)}
                      className="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 transition-colors whitespace-nowrap"
                    >
                      + Add
                    </button>
                  </div>
                ))}
              </div>
            )}

            {!suggestionsLoading && suggestions.length === 0 && (
              <button onClick={fetchSuggestions} className="btn-secondary">
                <Sparkles className="w-4 h-4 inline mr-2" />
                Get AI Suggestions
              </button>
            )}
          </div>
        )}
      </div>

      {/* Excel Import Modal */}
      <ExcelImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={() => {
          setShowImportModal(false)
          refetch()
        }}
      />

      {/* Social Media Discovery Modal */}
      <SocialDiscoveryModal
        isOpen={showSocialDiscovery}
        onClose={() => setShowSocialDiscovery(false)}
        onSuccess={() => {
          setShowSocialDiscovery(false)
          refetch()
        }}
      />
    </div>
  )
}

// ============ Source Card Component ============

function SourceCard({
  source,
  onToggle,
  onDelete,
  onAnalyze,
  showAnalyze,
  analyzeUrl,
  onAnalyzeUrlChange,
  onSubmitAnalyze,
  analyzing,
}: {
  source: any
  onToggle: () => void
  onDelete: () => void
  onAnalyze: () => void
  showAnalyze: boolean
  analyzeUrl: string
  onAnalyzeUrlChange: (url: string) => void
  onSubmitAnalyze: () => void
  analyzing: boolean
}) {
  return (
    <div className={`card p-4 ${!source.active ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-accent-900 truncate">{source.name}</h3>
          <p className="text-sm text-accent-500 truncate">{source.url}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          source.active
            ? 'bg-green-100 text-green-700'
            : 'bg-accent-100 text-accent-500'
        }`}>
          {source.active ? 'Active' : 'Paused'}
        </span>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs px-2 py-0.5 bg-accent-100 text-accent-700 rounded-full">
          {CATEGORY_LABELS[source.platform] || source.platform}
        </span>
        <span className="text-xs text-accent-500">
          {source.trend_count} trend{source.trend_count !== 1 ? 's' : ''}
        </span>
      </div>

      {source.target_demographics?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {source.target_demographics.map((d: string) => (
            <span key={d} className="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full">
              {DEMOGRAPHIC_LABELS[d as Demographic] || d}
            </span>
          ))}
        </div>
      )}

      {/* Analyze from source */}
      {showAnalyze && (
        <div className="mb-3 p-3 bg-accent-50 rounded-lg">
          <div className="flex gap-2">
            <input
              type="url"
              value={analyzeUrl}
              onChange={(e) => onAnalyzeUrlChange(e.target.value)}
              placeholder="Paste product URL to analyze..."
              className="input-base flex-1 text-sm"
            />
            <button
              onClick={onSubmitAnalyze}
              disabled={analyzing || !analyzeUrl}
              className="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {analyzing ? '...' : 'Go'}
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center gap-2 pt-3 border-t border-accent-100">
        <button
          onClick={onAnalyze}
          className="flex items-center gap-1 px-2 py-1 text-xs text-accent-600 hover:bg-accent-50 rounded transition-colors"
          title="Analyze a URL from this source"
        >
          <Search className="w-3.5 h-3.5" />
          Analyze
        </button>
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 px-2 py-1 text-xs text-accent-600 hover:bg-accent-50 rounded transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Visit
        </a>
        <button
          onClick={onToggle}
          className="flex items-center gap-1 px-2 py-1 text-xs text-accent-600 hover:bg-accent-50 rounded transition-colors"
          title={source.active ? 'Pause monitoring' : 'Resume monitoring'}
        >
          <Power className="w-3.5 h-3.5" />
          {source.active ? 'Pause' : 'Resume'}
        </button>
        <div className="flex-1" />
        <button
          onClick={onDelete}
          className="flex items-center gap-1 px-2 py-1 text-xs text-red-500 hover:bg-red-50 rounded transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
