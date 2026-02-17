import { useState, useEffect } from 'react'
import {
  Users, Search, Plus, ExternalLink, RefreshCw, Zap,
  ChevronDown, ChevronUp, Star, Instagram, Globe, Filter,
  Trash2, Eye, Play,
} from 'lucide-react'
import {
  listPeople, getPeopleStats, seedPeopleDatabase, scrapePerson, scrapeBatch,
  Person, PersonStats,
} from '@/api/people'

const TYPE_LABELS: Record<string, string> = {
  celebrity: 'Celebrity',
  influencer: 'Influencer',
  brand: 'Brand',
  media: 'Media',
  stylist: 'Stylist',
  editor: 'Editor',
}

const TYPE_COLORS: Record<string, string> = {
  celebrity: 'bg-purple-100 text-purple-700',
  influencer: 'bg-pink-100 text-pink-700',
  brand: 'bg-blue-100 text-blue-700',
  media: 'bg-amber-100 text-amber-700',
  stylist: 'bg-green-100 text-green-700',
  editor: 'bg-teal-100 text-teal-700',
}

const TIER_LABELS: Record<string, string> = {
  mega: 'Mega (10M+)',
  macro: 'Macro (1M-10M)',
  mid: 'Mid (100K-1M)',
  micro: 'Micro (10K-100K)',
  nano: 'Nano (<10K)',
}

const PLATFORM_ICONS: Record<string, string> = {
  instagram: 'IG',
  tiktok: 'TT',
  twitter: 'X',
  pinterest: 'Pin',
  youtube: 'YT',
}

function formatFollowers(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`
  if (count >= 1_000) return `${(count / 1_000).toFixed(0)}K`
  return String(count)
}

export default function People() {
  const [people, setPeople] = useState<Person[]>([])
  const [stats, setStats] = useState<PersonStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterTier, setFilterTier] = useState('')
  const [filterRegion, setFilterRegion] = useState('')
  const [filterPlatform, setFilterPlatform] = useState('')
  const [sortBy, setSortBy] = useState('relevance_score')
  const [showFilters, setShowFilters] = useState(false)

  // Seeding state
  const [seeding, setSeeding] = useState(false)
  const [seedResult, setSeedResult] = useState<string | null>(null)

  // Scraping state
  const [scrapingPersonId, setScrapingPersonId] = useState<number | null>(null)
  const [batchScraping, setBatchScraping] = useState(false)
  const [scrapeResult, setScrapeResult] = useState<string | null>(null)

  // Detail panel
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [peopleData, statsData] = await Promise.all([
        listPeople({
          type: filterType || undefined,
          tier: filterTier || undefined,
          region: filterRegion || undefined,
          platform: filterPlatform || undefined,
          search: searchQuery || undefined,
          sort_by: sortBy,
          limit: 200,
        }),
        getPeopleStats(),
      ])
      setPeople(peopleData)
      setStats(statsData)
    } catch (err) {
      console.error('Failed to fetch people:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [filterType, filterTier, filterRegion, filterPlatform, sortBy])

  // Debounced search
  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchData()
    }, 300)
    return () => clearTimeout(timeout)
  }, [searchQuery])

  const handleSeed = async () => {
    setSeeding(true)
    setSeedResult(null)
    try {
      const result = await seedPeopleDatabase()
      setSeedResult(`${result.created} people added (${result.skipped} already existed)`)
      fetchData()
    } catch (err: any) {
      setSeedResult(`Error: ${err?.response?.data?.detail || err.message}`)
    } finally {
      setSeeding(false)
    }
  }

  const handleScrape = async (personId: number) => {
    setScrapingPersonId(personId)
    setScrapeResult(null)
    try {
      const result = await scrapePerson(personId)
      const debugMsg = result.debug?.length ? ` | ${result.debug.join('; ')}` : ''
      setScrapeResult(`${result.person}: ${result.new_posts} new posts scraped${debugMsg}`)
      fetchData()
    } catch (err: any) {
      setScrapeResult(`Scrape failed: ${err?.response?.data?.detail || err.message}`)
    } finally {
      setScrapingPersonId(null)
    }
  }

  const handleBatchScrape = async () => {
    setBatchScraping(true)
    setScrapeResult(null)
    try {
      const result = await scrapeBatch({
        type: filterType || undefined,
        region: filterRegion || undefined,
        limit: 20,
      })
      setScrapeResult(
        `Batch complete: ${result.total_new_posts} new posts from ${result.total_people} people` +
        (result.errors.length > 0 ? ` (${result.errors.length} errors)` : '')
      )
      fetchData()
    } catch (err: any) {
      setScrapeResult(`Batch scrape failed: ${err?.response?.data?.detail || err.message}`)
    } finally {
      setBatchScraping(false)
    }
  }

  // Get unique regions from stats
  const regions = stats ? Object.keys(stats.by_region) : []

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
        <div>
          <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">
            People Database
          </h1>
          <p className="text-lg text-accent-600">
            Celebrities, influencers, brands, and media driving fashion trends
          </p>
        </div>
        <div className="flex items-center gap-3 mt-4 lg:mt-0">
          <button
            onClick={handleBatchScrape}
            disabled={batchScraping}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 transition-all shadow-sm disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${batchScraping ? 'animate-pulse' : ''}`} />
            {batchScraping ? 'Scraping...' : 'Scrape All'}
          </button>
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 transition-all shadow-sm disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 ${seeding ? 'animate-spin' : ''}`} />
            {seeding ? 'Seeding...' : 'Seed Database'}
          </button>
        </div>
      </div>

      {/* Result messages */}
      {seedResult && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 flex items-center justify-between">
          <span>{seedResult}</span>
          <button onClick={() => setSeedResult(null)} className="text-amber-600 hover:text-amber-800 ml-4">×</button>
        </div>
      )}
      {scrapeResult && (
        <div className="mb-6 p-4 rounded-xl bg-green-50 border border-green-200 text-green-800 flex items-center justify-between">
          <span>{scrapeResult}</span>
          <button onClick={() => setScrapeResult(null)} className="text-green-600 hover:text-green-800 ml-4">×</button>
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-accent-900">{stats.total_people}</p>
            <p className="text-sm text-accent-600">Total People</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{stats.active_count}</p>
            <p className="text-sm text-accent-600">Active</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-purple-600">{stats.by_type?.celebrity || 0}</p>
            <p className="text-sm text-accent-600">Celebrities</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-pink-600">{stats.by_type?.influencer || 0}</p>
            <p className="text-sm text-accent-600">Influencers</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{stats.by_type?.brand || 0}</p>
            <p className="text-sm text-accent-600">Brands</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-accent-600">{stats.total_platforms}</p>
            <p className="text-sm text-accent-600">Platform Handles</p>
          </div>
        </div>
      )}

      {/* Search & Filters */}
      <div className="card p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-accent-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search people by name..."
              className="input-base pl-10"
            />
          </div>
          <div className="flex gap-3">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-base"
            >
              <option value="relevance_score">Sort: Relevance</option>
              <option value="follower_count_total">Sort: Followers</option>
              <option value="name">Sort: Name</option>
              <option value="added_at">Sort: Newest</option>
            </select>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                showFilters ? 'bg-primary-50 border-primary-300 text-primary-700' : 'border-accent-200 text-accent-600 hover:border-accent-300'
              }`}
            >
              <Filter className="w-4 h-4" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-accent-100">
            <div>
              <label className="block text-sm font-medium text-accent-900 mb-1">Type</label>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="input-base">
                <option value="">All Types</option>
                {Object.entries(TYPE_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-accent-900 mb-1">Tier</label>
              <select value={filterTier} onChange={(e) => setFilterTier(e.target.value)} className="input-base">
                <option value="">All Tiers</option>
                {Object.entries(TIER_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-accent-900 mb-1">Region</label>
              <select value={filterRegion} onChange={(e) => setFilterRegion(e.target.value)} className="input-base">
                <option value="">All Regions</option>
                {regions.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-accent-900 mb-1">Platform</label>
              <select value={filterPlatform} onChange={(e) => setFilterPlatform(e.target.value)} className="input-base">
                <option value="">All Platforms</option>
                <option value="instagram">Instagram</option>
                <option value="tiktok">TikTok</option>
                <option value="twitter">X / Twitter</option>
                <option value="pinterest">Pinterest</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* People List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(9)].map((_, idx) => (
            <div key={idx} className="card h-48 bg-gradient-to-br from-accent-50 to-accent-100 animate-pulse" />
          ))}
        </div>
      ) : people.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {people.map((person) => (
            <PersonCard
              key={person.id}
              person={person}
              scraping={scrapingPersonId === person.id}
              onScrape={() => handleScrape(person.id)}
              onSelect={() => setSelectedPerson(selectedPerson?.id === person.id ? null : person)}
              isSelected={selectedPerson?.id === person.id}
            />
          ))}
        </div>
      ) : (
        <div className="card p-16 text-center">
          <Users className="w-12 h-12 text-accent-300 mx-auto mb-4" />
          <h3 className="text-2xl font-display font-bold text-accent-900 mb-2">No People Yet</h3>
          <p className="text-accent-600 mb-6">
            {searchQuery || filterType || filterTier
              ? 'No people match your filters. Try adjusting them.'
              : 'Seed the database with 70+ celebrities, influencers, and brands to get started.'}
          </p>
          {!searchQuery && !filterType && (
            <button onClick={handleSeed} disabled={seeding} className="btn-primary">
              <Zap className="w-4 h-4 inline mr-2" />
              Seed Database
            </button>
          )}
        </div>
      )}

      {/* Detail Panel */}
      {selectedPerson && (
        <PersonDetailPanel
          person={selectedPerson}
          onClose={() => setSelectedPerson(null)}
          onScrape={() => handleScrape(selectedPerson.id)}
          scraping={scrapingPersonId === selectedPerson.id}
        />
      )}
    </div>
  )
}


// ============ Person Card ============

function PersonCard({
  person,
  scraping,
  onScrape,
  onSelect,
  isSelected,
}: {
  person: Person
  scraping: boolean
  onScrape: () => void
  onSelect: () => void
  isSelected: boolean
}) {
  return (
    <div
      className={`card p-5 cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'ring-2 ring-primary-400 shadow-md' : ''
      } ${!person.active ? 'opacity-60' : ''}`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-accent-900 truncate text-lg">{person.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[person.type] || 'bg-accent-100 text-accent-700'}`}>
              {TYPE_LABELS[person.type] || person.type}
            </span>
            {person.tier && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-600">
                {person.tier}
              </span>
            )}
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-accent-900">{formatFollowers(person.follower_count_total)}</p>
          <p className="text-xs text-accent-500">followers</p>
        </div>
      </div>

      {/* Region */}
      {person.primary_region && (
        <div className="flex items-center gap-1 text-sm text-accent-500 mb-2">
          <Globe className="w-3.5 h-3.5" />
          <span>{person.primary_region}</span>
        </div>
      )}

      {/* Platforms */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {person.platforms?.map((p) => (
          <a
            key={p.id}
            href={p.profile_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 px-2 py-1 bg-accent-50 rounded text-xs text-accent-700 hover:bg-accent-100 transition-colors"
            title={`${p.platform}: @${p.handle} (${formatFollowers(p.follower_count)})`}
          >
            <span className="font-medium">{PLATFORM_ICONS[p.platform] || p.platform}</span>
            <span className="text-accent-500">@{p.handle}</span>
            {p.is_verified && <span className="text-blue-500" title="Verified">✓</span>}
          </a>
        ))}
      </div>

      {/* Style tags */}
      {person.style_tags && person.style_tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {person.style_tags.slice(0, 4).map((tag) => (
            <span key={tag} className="text-xs px-2 py-0.5 bg-primary-50 text-primary-600 rounded-full">
              {tag}
            </span>
          ))}
          {person.style_tags.length > 4 && (
            <span className="text-xs text-accent-400">+{person.style_tags.length - 4}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-accent-100">
        <div className="flex items-center gap-1">
          <Star className="w-4 h-4 text-amber-400" />
          <span className="text-sm font-medium text-accent-700">
            {Math.round(person.relevance_score)}
          </span>
          <span className="text-xs text-accent-400 ml-1">relevance</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); onScrape() }}
            disabled={scraping}
            className="flex items-center gap-1 px-2 py-1 text-xs text-accent-600 hover:bg-accent-50 rounded transition-colors disabled:opacity-50"
            title="Scrape latest posts"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${scraping ? 'animate-spin' : ''}`} />
            {scraping ? 'Scraping...' : 'Scrape'}
          </button>
        </div>
      </div>
    </div>
  )
}


// ============ Detail Panel ============

function PersonDetailPanel({ person, onClose, onScrape, scraping }: { person: Person; onClose: () => void; onScrape: () => void; scraping: boolean }) {
  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-2xl border-l border-accent-100 z-50 overflow-y-auto">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-display font-bold text-accent-900">{person.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-accent-50 rounded-lg transition-colors text-accent-600">
            ×
          </button>
        </div>

        {/* Scrape Button */}
        <button
          onClick={onScrape}
          disabled={scraping}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 mb-6 rounded-xl text-sm font-medium bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 transition-all shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
          {scraping ? 'Scraping latest posts...' : 'Scrape Latest Posts'}
        </button>

        {/* Type & Tier */}
        <div className="flex items-center gap-2 mb-4">
          <span className={`text-sm px-3 py-1 rounded-full font-medium ${TYPE_COLORS[person.type] || 'bg-accent-100 text-accent-700'}`}>
            {TYPE_LABELS[person.type] || person.type}
          </span>
          {person.tier && (
            <span className="text-sm px-3 py-1 rounded-full bg-accent-100 text-accent-600">
              {TIER_LABELS[person.tier] || person.tier}
            </span>
          )}
          <span className={`text-sm px-3 py-1 rounded-full ${person.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {person.active ? 'Active' : 'Inactive'}
          </span>
        </div>

        {/* Bio */}
        {person.bio && (
          <p className="text-sm text-accent-600 mb-4">{person.bio}</p>
        )}

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="text-center p-3 bg-accent-50 rounded-lg">
            <p className="text-xl font-bold text-accent-900">{formatFollowers(person.follower_count_total)}</p>
            <p className="text-xs text-accent-500">Total Followers</p>
          </div>
          <div className="text-center p-3 bg-accent-50 rounded-lg">
            <p className="text-xl font-bold text-accent-900">{Math.round(person.relevance_score)}</p>
            <p className="text-xs text-accent-500">Relevance</p>
          </div>
          <div className="text-center p-3 bg-accent-50 rounded-lg">
            <p className="text-xl font-bold text-accent-900">P{person.priority}</p>
            <p className="text-xs text-accent-500">Priority</p>
          </div>
        </div>

        {/* Region */}
        {person.primary_region && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-accent-900 mb-1">Region</h4>
            <p className="text-sm text-accent-600">
              {person.primary_region}
              {person.secondary_regions && person.secondary_regions.length > 0 && (
                <span className="text-accent-400"> + {person.secondary_regions.join(', ')}</span>
              )}
            </p>
          </div>
        )}

        {/* Demographics */}
        {person.demographics && person.demographics.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-accent-900 mb-1">Demographics</h4>
            <div className="flex flex-wrap gap-1">
              {person.demographics.map((d) => (
                <span key={d} className="text-xs px-2 py-1 bg-primary-50 text-primary-600 rounded-full">{d}</span>
              ))}
            </div>
          </div>
        )}

        {/* Style Tags */}
        {person.style_tags && person.style_tags.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-accent-900 mb-1">Style Tags</h4>
            <div className="flex flex-wrap gap-1">
              {person.style_tags.map((tag) => (
                <span key={tag} className="text-xs px-2 py-1 bg-pink-50 text-pink-600 rounded-full">{tag}</span>
              ))}
            </div>
          </div>
        )}

        {/* Categories */}
        {person.categories && person.categories.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-accent-900 mb-1">Categories</h4>
            <div className="flex flex-wrap gap-1">
              {person.categories.map((cat) => (
                <span key={cat} className="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded-full">{cat}</span>
              ))}
            </div>
          </div>
        )}

        {/* Platforms */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-accent-900 mb-2">Platforms</h4>
          <div className="space-y-2">
            {person.platforms?.map((p) => (
              <a
                key={p.id}
                href={p.profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-3 bg-accent-50 rounded-lg hover:bg-accent-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-bold text-sm text-accent-800 w-8">{PLATFORM_ICONS[p.platform] || p.platform}</span>
                  <div>
                    <span className="text-sm font-medium text-accent-900">@{p.handle}</span>
                    {p.is_verified && <span className="text-blue-500 ml-1">✓</span>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-accent-700">{formatFollowers(p.follower_count)}</span>
                  <ExternalLink className="w-4 h-4 text-accent-400" />
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* Metadata */}
        <div className="text-xs text-accent-400 pt-4 border-t border-accent-100 space-y-1">
          <p>Added: {new Date(person.added_at).toLocaleDateString()}</p>
          {person.last_scraped_at && (
            <p>Last scraped: {new Date(person.last_scraped_at).toLocaleString()}</p>
          )}
          <p>Scrape frequency: {person.scrape_frequency}</p>
          {person.notes && <p className="text-accent-500 italic mt-2">{person.notes}</p>}
        </div>
      </div>
    </div>
  )
}
