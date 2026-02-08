import { useState, useRef } from 'react'
import { Upload, X, CheckCircle, Loader, FileSpreadsheet } from 'lucide-react'
import ImportPreviewTable from './ImportPreviewTable'
import { DEMOGRAPHICS, DEMOGRAPHIC_LABELS, Demographic, SourceCreate } from '@/types'
import { createSourcesBulk } from '@/api/sources'

interface ParsedRow {
  name: string
  url: string
  index: number
}

interface ImportResult {
  succeeded: number
  failed: Array<{ name: string; url: string; reason: string }>
}

const SOURCE_CATEGORIES = [
  { value: 'ecommerce', label: 'Ecommerce Site' },
  { value: 'social', label: 'Social Media' },
  { value: 'media', label: 'Fashion Media / Magazine' },
  { value: 'search', label: 'Search & Trends' },
  { value: 'other', label: 'Other' },
]

export default function ExcelImportModal({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [parsedRows, setParsedRows] = useState<ParsedRow[]>([])
  const [defaultCategory, setDefaultCategory] = useState('ecommerce')
  const [defaultDemographics, setDefaultDemographics] = useState<string[]>(['junior_girls'])
  const [defaultFrequency, setDefaultFrequency] = useState('manual')
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [error, setError] = useState('')

  const parseFile = async (selectedFile: File) => {
    setError('')
    setFile(selectedFile)

    try {
      const XLSX = await import('xlsx')
      const buffer = await selectedFile.arrayBuffer()
      const workbook = XLSX.read(buffer, { type: 'array' })
      const sheet = workbook.Sheets[workbook.SheetNames[0]]
      const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as unknown[][]

      if (!rawData || rawData.length < 2) {
        setError('File must have a header row plus at least one data row.')
        setParsedRows([])
        return
      }

      // Skip header row, parse data rows
      const rows: ParsedRow[] = []
      const issues: string[] = []

      for (let i = 1; i < rawData.length; i++) {
        const row = rawData[i]
        if (!row || row.length === 0) continue // skip empty rows

        const name = String(row[0] || '').trim()
        let url = String(row[1] || '').trim()

        if (!name && !url) continue // skip fully empty rows

        if (!name) {
          issues.push(`Row ${i + 1}: missing site name`)
          continue
        }
        if (!url) {
          issues.push(`Row ${i + 1} (${name}): missing URL`)
          continue
        }

        // Auto-prepend https:// if missing protocol
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
          url = 'https://' + url
        }

        rows.push({ name, url, index: i })
      }

      if (rows.length === 0) {
        setError('No valid rows found. Make sure column A has site names and column B has URLs.')
        setParsedRows([])
        return
      }

      if (issues.length > 0) {
        setError(`${issues.length} row(s) skipped: ${issues.slice(0, 3).join('; ')}${issues.length > 3 ? '...' : ''}`)
      }

      setParsedRows(rows)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to parse file'
      setError(`Could not read file: ${msg}`)
      setParsedRows([])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) parseFile(selectedFile)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) parseFile(droppedFile)
  }

  const handleImport = async () => {
    if (parsedRows.length === 0) return

    setImporting(true)
    setError('')

    try {
      const sources: SourceCreate[] = parsedRows.map((row) => ({
        url: row.url,
        platform: defaultCategory,
        name: row.name,
        target_demographics: defaultDemographics,
        frequency: defaultFrequency,
      }))

      const response = await createSourcesBulk(sources)
      setResult(response)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Import failed. Please try again.')
    } finally {
      setImporting(false)
    }
  }

  const toggleDemographic = (demo: string) => {
    setDefaultDemographics((prev) =>
      prev.includes(demo) ? prev.filter((d) => d !== demo) : [...prev, demo]
    )
  }

  const handleClose = () => {
    if (result && result.succeeded > 0) {
      onSuccess()
    }
    // Reset state
    setFile(null)
    setParsedRows([])
    setResult(null)
    setError('')
    setDefaultCategory('ecommerce')
    setDefaultDemographics(['junior_girls'])
    setDefaultFrequency('manual')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-accent-200 px-6 py-4 flex items-center justify-between rounded-t-xl">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-display font-bold text-accent-900">Import Sources from Excel</h2>
          </div>
          <button onClick={handleClose} className="text-accent-400 hover:text-accent-600 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Result screen */}
          {result && (
            <div className="text-center space-y-4 py-4">
              <CheckCircle className="w-14 h-14 text-green-500 mx-auto" />
              <div>
                <p className="text-2xl font-bold text-accent-900">
                  {result.succeeded} source{result.succeeded !== 1 ? 's' : ''} imported
                </p>
                {result.failed.length > 0 && (
                  <p className="text-sm text-accent-600 mt-1">
                    {result.failed.length} skipped
                  </p>
                )}
              </div>

              {result.failed.length > 0 && (
                <div className="text-left mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-amber-800 mb-2">Skipped items:</p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {result.failed.map((item, idx) => (
                      <p key={idx} className="text-sm text-amber-700">
                        <span className="font-medium">{item.name || item.url}</span>: {item.reason}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              <button onClick={handleClose} className="btn-primary px-8">
                Done
              </button>
            </div>
          )}

          {/* Import form */}
          {!result && (
            <>
              {/* File drop zone */}
              <div
                className="border-2 border-dashed border-accent-300 rounded-xl p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-10 h-10 text-accent-400 mx-auto mb-3" />
                {file ? (
                  <div>
                    <p className="text-accent-900 font-medium">{file.name}</p>
                    <p className="text-sm text-accent-500 mt-1">
                      {parsedRows.length} site{parsedRows.length !== 1 ? 's' : ''} ready to import
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-accent-900 font-medium mb-1">
                      Drop your Excel or CSV file here
                    </p>
                    <p className="text-sm text-accent-500">
                      Column A: Site Name &nbsp;|&nbsp; Column B: URL
                    </p>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* Preview */}
              {parsedRows.length > 0 && (
                <>
                  <ImportPreviewTable rows={parsedRows} />

                  {/* Default settings */}
                  <div className="space-y-4 bg-accent-50 rounded-lg p-4">
                    <p className="text-sm font-medium text-accent-900">
                      Apply to all {parsedRows.length} sources:
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-accent-700 mb-1">Category</label>
                        <select
                          value={defaultCategory}
                          onChange={(e) => setDefaultCategory(e.target.value)}
                          className="input-base"
                        >
                          {SOURCE_CATEGORIES.map((c) => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-accent-700 mb-1">Check Frequency</label>
                        <select
                          value={defaultFrequency}
                          onChange={(e) => setDefaultFrequency(e.target.value)}
                          className="input-base"
                        >
                          <option value="manual">Manual</option>
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-accent-700 mb-2">Target Demographics</label>
                      <div className="flex flex-wrap gap-2">
                        {DEMOGRAPHICS.map((demo) => (
                          <button
                            key={demo}
                            type="button"
                            onClick={() => toggleDemographic(demo)}
                            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                              defaultDemographics.includes(demo)
                                ? 'bg-primary-100 border-primary-300 text-primary-700'
                                : 'bg-white border-accent-200 text-accent-600 hover:border-accent-300'
                            }`}
                          >
                            {DEMOGRAPHIC_LABELS[demo as Demographic]}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={handleImport}
                  disabled={parsedRows.length === 0 || importing}
                  className="btn-primary flex items-center gap-2 flex-1 justify-center"
                >
                  {importing ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Importing {parsedRows.length} sources...
                    </>
                  ) : parsedRows.length > 0 ? (
                    `Import ${parsedRows.length} Source${parsedRows.length !== 1 ? 's' : ''}`
                  ) : (
                    'Select a file to import'
                  )}
                </button>
                <button onClick={handleClose} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
