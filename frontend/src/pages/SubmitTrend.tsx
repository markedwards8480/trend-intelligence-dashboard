import { useState } from 'react'
import { AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { submitTrend } from '@/api/trends'
import { TrendItem } from '@/types'

const mockAnalysis: Partial<TrendItem> = {
  category: 'Dresses',
  colors: ['pink', 'white', 'beige'],
  style_tags: ['Y2K', 'Maxi', 'Summer Vibes'],
  ai_analysis:
    'This trend combines nostalgic Y2K aesthetics with modern minimalism. The soft color palette (pink, white, beige) appeals strongly to the 15-28 age demographic. The maxi silhouette offers comfort while maintaining style, making it highly shareable on social media.',
}

export default function SubmitTrend() {
  const [url, setUrl] = useState('')
  const [platform, setPlatform] = useState('Instagram')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<Partial<TrendItem> | null>(null)

  const platforms = ['Instagram', 'TikTok', 'SHEIN', 'Fashion Nova', 'Princess Polly', 'Zara', 'H&M', 'Other']

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)
    setAnalysisResult(null)

    if (!url.trim()) {
      setError('Please enter a valid URL')
      return
    }

    setLoading(true)

    try {
      const result = await submitTrend({
        url: url.trim(),
        platform,
      })

      setAnalysisResult(result as Partial<TrendItem>)
      setSuccess(true)
      setUrl('')

      setTimeout(() => {
        setSuccess(false)
        setAnalysisResult(null)
      }, 8000)
    } catch (err: any) {
      // Show real error instead of hiding it
      const message = err?.response?.data?.detail || err?.message || 'Failed to analyze trend. Please try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl lg:text-5xl font-display font-bold text-accent-900 mb-2">Submit a Trend</h1>
        <p className="text-lg text-accent-600">Paste a link to analyze fashion trends in real-time</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="card p-8">
            {/* URL Input */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-accent-900 mb-3">Product/Post URL</label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://instagram.com/p/..."
                className="input-base text-lg py-3"
                disabled={loading}
              />
              <p className="text-xs text-accent-500 mt-2">
                Works with Instagram, TikTok, SHEIN, and other major fashion platforms
              </p>
            </div>

            {/* Platform Selector */}
            <div className="mb-8">
              <label className="block text-sm font-semibold text-accent-900 mb-3">Platform</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {platforms.map((plat) => (
                  <button
                    key={plat}
                    type="button"
                    onClick={() => setPlatform(plat)}
                    className={`px-4 py-3 rounded-lg font-medium transition-all duration-200 border-2 ${
                      platform === plat
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-accent-200 bg-white text-accent-700 hover:border-primary-400'
                    }`}
                  >
                    {plat}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button type="submit" disabled={loading} className="w-full btn-primary py-4 text-lg font-semibold">
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <Loader className="w-5 h-5 animate-spin" />
                  Analyzing trend...
                </div>
              ) : (
                'Submit & Analyze'
              )}
            </button>

            {/* Info Box */}
            <div className="mt-8 p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <h3 className="font-semibold text-primary-900 mb-2">What happens next?</h3>
              <ul className="text-sm text-primary-800 space-y-1">
                <li>✓ AI analyzes the image and metadata</li>
                <li>✓ Extracts category, colors, and style tags</li>
                <li>✓ Calculates trend score based on engagement</li>
                <li>✓ Generates insight narrative</li>
              </ul>
            </div>
          </form>
        </div>

        {/* Analysis Result / Quick Tips */}
        <div>
          {analysisResult ? (
            <div className="card p-8 border-l-4 border-l-primary-600 sticky top-8">
              <div className="flex items-start gap-3 mb-4">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                <div>
                  <h3 className="font-display font-bold text-accent-900">Analysis Complete!</h3>
                  <p className="text-sm text-accent-600">Your trend has been processed</p>
                </div>
              </div>

              <div className="space-y-6">
                {/* Category */}
                {analysisResult.category && (
                  <div>
                    <p className="text-xs font-semibold text-accent-600 uppercase tracking-wide mb-2">Category</p>
                    <p className="text-lg font-display font-bold text-accent-900">{analysisResult.category}</p>
                  </div>
                )}

                {/* Colors */}
                {analysisResult.colors && analysisResult.colors.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-accent-600 uppercase tracking-wide mb-3">Colors</p>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.colors.map((color, idx) => (
                        <span key={idx} className="badge badge-primary">
                          {color}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Style Tags */}
                {analysisResult.style_tags && analysisResult.style_tags.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-accent-600 uppercase tracking-wide mb-3">Style Tags</p>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.style_tags.map((tag, idx) => (
                        <span key={idx} className="badge-accent text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Analysis */}
                {analysisResult.ai_analysis && (
                  <div>
                    <p className="text-xs font-semibold text-accent-600 uppercase tracking-wide mb-2">Analysis</p>
                    <p className="text-sm leading-relaxed text-accent-700">{analysisResult.ai_analysis}</p>
                  </div>
                )}
              </div>

              <button
                onClick={() => setAnalysisResult(null)}
                className="w-full btn-secondary mt-6"
              >
                Submit Another
              </button>
            </div>
          ) : (
            <div className="sticky top-8 space-y-4">
              {/* Tips */}
              <div className="card p-6">
                <h3 className="font-display font-bold text-accent-900 mb-4">💡 Pro Tips</h3>
                <ul className="space-y-3 text-sm text-accent-700">
                  <li className="flex gap-2">
                    <span className="text-primary-600 font-bold">1.</span>
                    <span>Use direct product links for best results</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary-600 font-bold">2.</span>
                    <span>Include high-engagement posts for accurate scoring</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary-600 font-bold">3.</span>
                    <span>Fashion-forward items get higher trend scores</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary-600 font-bold">4.</span>
                    <span>Save to mood boards for curated collections</span>
                  </li>
                </ul>
              </div>

              {/* Recent Platforms */}
              <div className="card p-6">
                <h3 className="font-display font-bold text-accent-900 mb-4">📱 Supported Platforms</h3>
                <div className="space-y-2 text-sm">
                  <p className="flex items-center gap-2 text-accent-700">
                    <span className="text-lg">📸</span> Instagram & Reels
                  </p>
                  <p className="flex items-center gap-2 text-accent-700">
                    <span className="text-lg">🎬</span> TikTok
                  </p>
                  <p className="flex items-center gap-2 text-accent-700">
                    <span className="text-lg">🛍️</span> SHEIN & Fashion Nova
                  </p>
                  <p className="flex items-center gap-2 text-accent-700">
                    <span className="text-lg">👗</span> Zara & H&M
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
