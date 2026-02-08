import { useState } from 'react'
import { X, Loader, Sparkles, ExternalLink, Plus, CheckCircle, Hash, Users, Instagram } from 'lucide-react'
import { BrandSocialDiscovery, SocialAccount, SocialDiscoveryResponse, SourceCreate } from '@/types'
import { discoverSocialAccounts, createSourcesBulk } from '@/api/sources'

// Simple TikTok icon component
function TikTokIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.51a8.27 8.27 0 004.76 1.5V6.56a4.84 4.84 0 01-1-.13z" />
    </svg>
  )
}

function PlatformIcon({ platform, className }: { platform: string; className?: string }) {
  if (platform === 'tiktok') return <TikTokIcon className={className} />
  if (platform === 'instagram') return <Instagram className={className} />
  return <Users className={className} />
}

function PlatformBadge({ platform }: { platform: string }) {
  const colors = platform === 'tiktok'
    ? 'bg-gray-900 text-white'
    : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${colors}`}>
      <PlatformIcon platform={platform} className="w-3 h-3" />
      {platform === 'tiktok' ? 'TikTok' : 'Instagram'}
    </span>
  )
}

interface SelectedAccount {
  key: string
  account: SocialAccount
  brand: string
}

export default function SocialDiscoveryModal({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<SocialDiscoveryResponse | null>(null)
  const [error, setError] = useState('')
  const [selectedAccounts, setSelectedAccounts] = useState<Map<string, SelectedAccount>>(new Map())
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{ succeeded: number; failed: number } | null>(null)
  const [expandedBrand, setExpandedBrand] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'brands' | 'all-accounts' | 'influencers'>('brands')

  const handleDiscover = async () => {
    setLoading(true)
    setError('')
    setData(null)
    try {
      const result = await discoverSocialAccounts()
      setData(result)
      // Auto-expand first brand
      if (result.brands.length > 0) {
        setExpandedBrand(result.brands[0].brand)
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Discovery failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const accountKey = (account: SocialAccount, brand: string) =>
    `${brand}:${account.platform}:${account.handle}`

  const toggleAccount = (account: SocialAccount, brand: string) => {
    const key = accountKey(account, brand)
    setSelectedAccounts((prev) => {
      const next = new Map(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.set(key, { key, account, brand })
      }
      return next
    })
  }

  const selectAllOfficial = () => {
    if (!data) return
    const next = new Map(selectedAccounts)
    for (const brand of data.brands) {
      for (const account of brand.accounts) {
        const key = accountKey(account, brand.brand)
        if (!next.has(key)) {
          next.set(key, { key, account, brand: brand.brand })
        }
      }
    }
    setSelectedAccounts(next)
  }

  const selectAllInfluencers = () => {
    if (!data) return
    const next = new Map(selectedAccounts)
    for (const brand of data.brands) {
      for (const inf of brand.related_influencers) {
        const key = accountKey(inf, brand.brand)
        if (!next.has(key)) {
          next.set(key, { key, account: inf, brand: brand.brand })
        }
      }
    }
    setSelectedAccounts(next)
  }

  const handleImportSelected = async () => {
    if (selectedAccounts.size === 0) return
    setImporting(true)
    setError('')

    try {
      const sources: SourceCreate[] = Array.from(selectedAccounts.values()).map(({ account }) => ({
        url: account.url,
        platform: 'social',
        name: account.name || `${account.handle} (${account.platform})`,
        target_demographics: ['junior_girls', 'young_women'],
        frequency: 'manual',
      }))

      const result = await createSourcesBulk(sources)
      setImportResult({
        succeeded: result.succeeded,
        failed: result.failed.length,
      })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Import failed. Please try again.')
    } finally {
      setImporting(false)
    }
  }

  const handleClose = () => {
    if (importResult && importResult.succeeded > 0) {
      onSuccess()
    }
    setData(null)
    setSelectedAccounts(new Map())
    setImportResult(null)
    setError('')
    setExpandedBrand(null)
    setActiveTab('brands')
    onClose()
  }

  if (!isOpen) return null

  // Collect all accounts and influencers across brands
  const allAccounts = data?.brands.flatMap((b) =>
    b.accounts.map((a) => ({ ...a, brand: b.brand }))
  ) || []
  const allInfluencers = data?.brands.flatMap((b) =>
    b.related_influencers.map((a) => ({ ...a, brand: b.brand }))
  ) || []

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-accent-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-display font-bold text-accent-900">Social Media Discovery</h2>
              <p className="text-sm text-accent-500">Find TikTok & Instagram accounts for your brands</p>
            </div>
          </div>
          <button onClick={handleClose} className="text-accent-400 hover:text-accent-600 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Import result */}
          {importResult && (
            <div className="text-center space-y-4 py-8">
              <CheckCircle className="w-14 h-14 text-green-500 mx-auto" />
              <div>
                <p className="text-2xl font-bold text-accent-900">
                  {importResult.succeeded} account{importResult.succeeded !== 1 ? 's' : ''} added
                </p>
                {importResult.failed > 0 && (
                  <p className="text-sm text-accent-600 mt-1">
                    {importResult.failed} skipped (already exist)
                  </p>
                )}
              </div>
              <p className="text-accent-600">
                These social media accounts are now in your Sources and ready to monitor.
              </p>
              <button onClick={handleClose} className="btn-primary px-8">
                Done
              </button>
            </div>
          )}

          {/* Initial state — show discover button */}
          {!data && !loading && !importResult && (
            <div className="text-center py-12 space-y-6">
              <div className="flex items-center justify-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-gray-900 flex items-center justify-center">
                  <TikTokIcon className="w-8 h-8 text-white" />
                </div>
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 flex items-center justify-center">
                  <Instagram className="w-8 h-8 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-bold text-accent-900 mb-2">
                  Discover Social Media Accounts
                </h3>
                <p className="text-accent-600 max-w-lg mx-auto">
                  AI will analyze your 40 ecommerce brands and find their official TikTok and Instagram accounts,
                  plus related fashion influencers and creators who feature these brands.
                </p>
              </div>
              <button
                onClick={handleDiscover}
                className="btn-primary px-8 py-3 text-lg flex items-center gap-2 mx-auto"
              >
                <Sparkles className="w-5 h-5" />
                Discover Accounts
              </button>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="text-center py-16 space-y-4">
              <Loader className="w-12 h-12 text-primary-600 animate-spin mx-auto" />
              <div>
                <p className="text-lg font-medium text-accent-900">Discovering social media accounts...</p>
                <p className="text-sm text-accent-500 mt-1">
                  AI is analyzing your ecommerce brands and finding TikTok & Instagram accounts.
                  This may take 30-60 seconds.
                </p>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Results */}
          {data && !importResult && (
            <>
              {/* Stats bar */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-accent-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-accent-900">{data.brands.length}</p>
                  <p className="text-sm text-accent-600">Brands Analyzed</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-purple-700">{data.total_accounts}</p>
                  <p className="text-sm text-purple-600">Official Accounts</p>
                </div>
                <div className="bg-pink-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-pink-700">{data.total_influencers}</p>
                  <p className="text-sm text-pink-600">Influencer Accounts</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 mb-4 bg-accent-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('brands')}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'brands' ? 'bg-white shadow text-accent-900' : 'text-accent-600 hover:text-accent-900'
                  }`}
                >
                  By Brand ({data.brands.length})
                </button>
                <button
                  onClick={() => setActiveTab('all-accounts')}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'all-accounts' ? 'bg-white shadow text-accent-900' : 'text-accent-600 hover:text-accent-900'
                  }`}
                >
                  All Accounts ({allAccounts.length})
                </button>
                <button
                  onClick={() => setActiveTab('influencers')}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'influencers' ? 'bg-white shadow text-accent-900' : 'text-accent-600 hover:text-accent-900'
                  }`}
                >
                  Influencers ({allInfluencers.length})
                </button>
              </div>

              {/* Quick select buttons */}
              <div className="flex gap-2 mb-4">
                <button onClick={selectAllOfficial} className="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors">
                  Select All Official
                </button>
                <button onClick={selectAllInfluencers} className="text-xs px-3 py-1.5 bg-pink-100 text-pink-700 rounded-full hover:bg-pink-200 transition-colors">
                  Select All Influencers
                </button>
                {selectedAccounts.size > 0 && (
                  <button
                    onClick={() => setSelectedAccounts(new Map())}
                    className="text-xs px-3 py-1.5 bg-accent-100 text-accent-600 rounded-full hover:bg-accent-200 transition-colors"
                  >
                    Clear Selection ({selectedAccounts.size})
                  </button>
                )}
              </div>

              {/* Brand-by-brand view */}
              {activeTab === 'brands' && (
                <div className="space-y-2">
                  {data.brands.map((brand) => (
                    <BrandSection
                      key={brand.brand}
                      brand={brand}
                      expanded={expandedBrand === brand.brand}
                      onToggle={() => setExpandedBrand(expandedBrand === brand.brand ? null : brand.brand)}
                      selectedAccounts={selectedAccounts}
                      onToggleAccount={toggleAccount}
                      accountKey={accountKey}
                    />
                  ))}
                </div>
              )}

              {/* All accounts view */}
              {activeTab === 'all-accounts' && (
                <div className="space-y-2">
                  {allAccounts.map((account) => (
                    <AccountRow
                      key={`${account.brand}:${account.platform}:${account.handle}`}
                      account={account}
                      brand={account.brand}
                      selected={selectedAccounts.has(accountKey(account, account.brand))}
                      onToggle={() => toggleAccount(account, account.brand)}
                    />
                  ))}
                </div>
              )}

              {/* Influencers view */}
              {activeTab === 'influencers' && (
                <div className="space-y-2">
                  {allInfluencers.map((inf) => (
                    <AccountRow
                      key={`${inf.brand}:${inf.platform}:${inf.handle}`}
                      account={inf}
                      brand={inf.brand}
                      selected={selectedAccounts.has(accountKey(inf, inf.brand))}
                      onToggle={() => toggleAccount(inf, inf.brand)}
                      showBrand
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer — import bar */}
        {data && !importResult && (
          <div className="border-t border-accent-200 px-6 py-4 bg-accent-50 flex items-center justify-between">
            <p className="text-sm text-accent-600">
              {selectedAccounts.size > 0 ? (
                <><strong>{selectedAccounts.size}</strong> account{selectedAccounts.size !== 1 ? 's' : ''} selected</>
              ) : (
                'Select accounts to add to your Sources'
              )}
            </p>
            <div className="flex gap-3">
              <button onClick={handleClose} className="btn-secondary">
                Cancel
              </button>
              <button
                onClick={handleImportSelected}
                disabled={selectedAccounts.size === 0 || importing}
                className="btn-primary flex items-center gap-2"
              >
                {importing ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Add {selectedAccounts.size} Account{selectedAccounts.size !== 1 ? 's' : ''}
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Sub-components ============

function BrandSection({
  brand,
  expanded,
  onToggle,
  selectedAccounts,
  onToggleAccount,
  accountKey,
}: {
  brand: BrandSocialDiscovery
  expanded: boolean
  onToggle: () => void
  selectedAccounts: Map<string, SelectedAccount>
  onToggleAccount: (account: SocialAccount, brand: string) => void
  accountKey: (account: SocialAccount, brand: string) => string
}) {
  const totalAccounts = brand.accounts.length + brand.related_influencers.length
  const selectedCount = [...brand.accounts, ...brand.related_influencers].filter(
    (a) => selectedAccounts.has(accountKey(a, brand.brand))
  ).length

  return (
    <div className="border border-accent-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-white hover:bg-accent-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="font-bold text-accent-900">{brand.brand}</span>
          <span className="text-xs text-accent-500">
            {totalAccounts} account{totalAccounts !== 1 ? 's' : ''}
          </span>
          {selectedCount > 0 && (
            <span className="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">
              {selectedCount} selected
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {brand.accounts.map((a) => (
            <PlatformBadge key={a.platform + a.handle} platform={a.platform} />
          ))}
        </div>
      </button>

      {expanded && (
        <div className="border-t border-accent-200 bg-accent-50/50 p-4 space-y-3">
          {/* Official accounts */}
          {brand.accounts.length > 0 && (
            <div>
              <p className="text-xs font-medium text-accent-500 uppercase tracking-wider mb-2">Official Accounts</p>
              <div className="space-y-2">
                {brand.accounts.map((account) => (
                  <AccountRow
                    key={account.platform + account.handle}
                    account={account}
                    brand={brand.brand}
                    selected={selectedAccounts.has(accountKey(account, brand.brand))}
                    onToggle={() => onToggleAccount(account, brand.brand)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Related influencers */}
          {brand.related_influencers.length > 0 && (
            <div>
              <p className="text-xs font-medium text-accent-500 uppercase tracking-wider mb-2">Related Influencers</p>
              <div className="space-y-2">
                {brand.related_influencers.map((inf) => (
                  <AccountRow
                    key={inf.platform + inf.handle}
                    account={inf}
                    brand={brand.brand}
                    selected={selectedAccounts.has(accountKey(inf, brand.brand))}
                    onToggle={() => onToggleAccount(inf, brand.brand)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Hashtags */}
          {brand.hashtags.length > 0 && (
            <div>
              <p className="text-xs font-medium text-accent-500 uppercase tracking-wider mb-2">Hashtags</p>
              <div className="flex flex-wrap gap-2">
                {brand.hashtags.map((tag) => (
                  <span key={tag} className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                    <Hash className="w-3 h-3" />
                    {tag.replace('#', '')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function AccountRow({
  account,
  brand,
  selected,
  onToggle,
  showBrand,
}: {
  account: SocialAccount & { brand?: string }
  brand: string
  selected: boolean
  onToggle: () => void
  showBrand?: boolean
}) {
  return (
    <div
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
        selected ? 'bg-primary-50 border border-primary-200' : 'bg-white border border-accent-200 hover:border-accent-300'
      }`}
      onClick={onToggle}
    >
      <input
        type="checkbox"
        checked={selected}
        onChange={onToggle}
        className="w-4 h-4 text-primary-600 rounded border-accent-300"
        onClick={(e) => e.stopPropagation()}
      />
      <PlatformBadge platform={account.platform} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-accent-900 text-sm">{account.handle}</span>
          {account.estimated_followers && (
            <span className="text-xs text-accent-400">{account.estimated_followers} followers</span>
          )}
          {showBrand && (
            <span className="text-xs px-2 py-0.5 bg-accent-100 text-accent-600 rounded-full">{brand}</span>
          )}
        </div>
        {account.description && (
          <p className="text-xs text-accent-500 truncate">{account.description}</p>
        )}
      </div>
      <a
        href={account.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-accent-400 hover:text-primary-600 transition-colors"
        onClick={(e) => e.stopPropagation()}
      >
        <ExternalLink className="w-4 h-4" />
      </a>
    </div>
  )
}
