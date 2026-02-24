import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useLaunchesStore } from '@/stores/launches'

vi.mock('@/api', () => ({
  fetchLaunches: vi.fn(),
}))

import { fetchLaunches } from '@/api'
const mockFetchLaunches = vi.mocked(fetchLaunches)

describe('useLaunchesStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct default state', () => {
    const store = useLaunchesStore()
    expect(store.items).toEqual([])
    expect(store.total).toBe(0)
    expect(store.page).toBe(1)
    expect(store.limit).toBe(20)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.filters).toEqual({ success: null, upcoming: null, rocket_id: null })
  })

  it('load sets items on success', async () => {
    mockFetchLaunches.mockResolvedValue({
      items: [{ id: 'l1', name: 'Test' }] as any,
      total: 1,
      page: 1,
      limit: 20,
    })
    const store = useLaunchesStore()
    await store.load()
    expect(store.items).toHaveLength(1)
    expect(store.total).toBe(1)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load sets error on failure', async () => {
    mockFetchLaunches.mockRejectedValue(new Error('Network error'))
    const store = useLaunchesStore()
    await store.load()
    expect(store.error).toBe('Failed to load launches')
    expect(store.items).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('setPage updates page and calls load', async () => {
    mockFetchLaunches.mockResolvedValue({ items: [], total: 0, page: 2, limit: 20 })
    const store = useLaunchesStore()
    await store.setPage(2)
    expect(store.page).toBe(2)
  })

  it('setFilters merges filters and resets page', async () => {
    mockFetchLaunches.mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 })
    const store = useLaunchesStore()
    store.page = 3
    await store.setFilters({ success: true })
    expect(store.filters.success).toBe(true)
    expect(store.page).toBe(1)
  })

  it('passes filters to API call', async () => {
    mockFetchLaunches.mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 })
    const store = useLaunchesStore()
    store.filters.success = true
    store.filters.rocket_id = 'r1'
    await store.load()
    expect(mockFetchLaunches).toHaveBeenCalledWith(
      expect.objectContaining({ success: true, rocket_id: 'r1', page: 1, limit: 20 })
    )
  })
})
