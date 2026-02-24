import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRocketsStore } from '@/stores/rockets'

vi.mock('@/api', () => ({
  fetchRockets: vi.fn(),
}))

import { fetchRockets } from '@/api'
const mockFetchRockets = vi.mocked(fetchRockets)

describe('useRocketsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct default state', () => {
    const store = useRocketsStore()
    expect(store.items).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load fetches rockets', async () => {
    const fakeRockets = [
      { id: 'r1', name: 'Falcon 9' },
      { id: 'r2', name: 'Falcon Heavy' },
    ] as any
    mockFetchRockets.mockResolvedValue(fakeRockets)

    const store = useRocketsStore()
    await store.load()
    expect(store.items).toHaveLength(2)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load sets error on failure', async () => {
    mockFetchRockets.mockRejectedValue(new Error('timeout'))
    const store = useRocketsStore()
    await store.load()
    expect(store.error).toBe('Failed to load rockets')
    expect(store.items).toEqual([])
  })
})
