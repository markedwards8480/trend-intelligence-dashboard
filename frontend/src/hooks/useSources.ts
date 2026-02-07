import { useState, useEffect, useCallback } from 'react'
import { Source, SourceCreate, SourceUpdate, SourceSuggestion } from '@/types'
import * as sourcesApi from '@/api/sources'

export const useSources = () => {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSources = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await sourcesApi.getSources()
      setSources(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sources')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSources()
  }, [fetchSources])

  const addSource = async (data: SourceCreate) => {
    const newSource = await sourcesApi.createSource(data)
    setSources((prev) => [newSource, ...prev])
    return newSource
  }

  const updateSource = async (id: number, data: SourceUpdate) => {
    const updated = await sourcesApi.updateSource(id, data)
    setSources((prev) => prev.map((s) => (s.id === id ? updated : s)))
    return updated
  }

  const removeSource = async (id: number) => {
    await sourcesApi.deleteSource(id)
    setSources((prev) => prev.filter((s) => s.id !== id))
  }

  const toggleSource = async (id: number, active: boolean) => {
    return updateSource(id, { active })
  }

  return { sources, loading, error, addSource, updateSource, removeSource, toggleSource, refetch: fetchSources }
}

export const useSourceSuggestions = () => {
  const [suggestions, setSuggestions] = useState<SourceSuggestion[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSuggestions = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await sourcesApi.getSuggestions()
      setSuggestions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get suggestions')
    } finally {
      setLoading(false)
    }
  }

  return { suggestions, loading, error, fetchSuggestions }
}
