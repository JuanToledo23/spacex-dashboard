import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useStarlinkStore } from '@/stores/starlink'

vi.mock('@/api', () => ({
  fetchStarlink: vi.fn(),
}))

import { fetchStarlink } from '@/api'
const mockFetchStarlink = vi.mocked(fetchStarlink)

describe('useStarlinkStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct default state', () => {
    const store = useStarlinkStore()
    expect(store.items).toEqual([])
    expect(store.version).toBeNull()
    expect(store.page).toBe(1)
  })

  it('load fetches starlink data', async () => {
    mockFetchStarlink.mockResolvedValue({
      items: [{ id: 's1' }] as any,
      total: 1,
      page: 1,
      limit: 20,
    })
    const store = useStarlinkStore()
    await store.load()
    expect(store.items).toHaveLength(1)
    expect(store.loading).toBe(false)
  })

  it('load sets error on failure', async () => {
    mockFetchStarlink.mockRejectedValue(new Error('fail'))
    const store = useStarlinkStore()
    await store.load()
    expect(store.error).toBeTruthy()
  })

  it('setVersion updates version and resets page', async () => {
    mockFetchStarlink.mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 })
    const store = useStarlinkStore()
    store.page = 5
    await store.setVersion('v2.0')
    expect(store.version).toBe('v2.0')
    expect(store.page).toBe(1)
  })

  it('setPage updates page and loads', async () => {
    mockFetchStarlink.mockResolvedValue({ items: [], total: 0, page: 3, limit: 20 })
    const store = useStarlinkStore()
    await store.setPage(3)
    expect(store.page).toBe(3)
  })

  it('includes version in API call when set', async () => {
    mockFetchStarlink.mockResolvedValue({ items: [], total: 0, page: 1, limit: 20 })
    const store = useStarlinkStore()
    store.version = 'v1.5'
    await store.load()
    expect(mockFetchStarlink).toHaveBeenCalledWith(
      expect.objectContaining({ version: 'v1.5' })
    )
  })
})
