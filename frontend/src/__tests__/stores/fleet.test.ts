import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFleetStore } from '@/stores/fleet'

vi.mock('@/api', () => ({
  fetchFleetStats: vi.fn(),
  fetchRockets: vi.fn(),
}))

import { fetchFleetStats, fetchRockets } from '@/api'
const mockFetchFleetStats = vi.mocked(fetchFleetStats)
const mockFetchRockets = vi.mocked(fetchRockets)

describe('useFleetStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct default state', () => {
    const store = useFleetStore()
    expect(store.stats).toBeNull()
    expect(store.rockets).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load fetches fleet stats and rockets', async () => {
    const fakeStats = { total_cores: 10 } as any
    const fakeRockets = [{ id: 'r1', name: 'Falcon 9' }] as any
    mockFetchFleetStats.mockResolvedValue(fakeStats)
    mockFetchRockets.mockResolvedValue(fakeRockets)

    const store = useFleetStore()
    await store.load()
    expect(store.stats).toEqual(fakeStats)
    expect(store.rockets).toEqual(fakeRockets)
    expect(store.loading).toBe(false)
  })

  it('load sets error on failure', async () => {
    mockFetchFleetStats.mockRejectedValue(new Error('API down'))
    mockFetchRockets.mockResolvedValue([])

    const store = useFleetStore()
    await store.load()
    expect(store.error).toBe('Failed to load fleet data')
    expect(store.loading).toBe(false)
  })
})
