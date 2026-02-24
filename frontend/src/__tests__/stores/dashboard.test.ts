import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDashboardStore } from '@/stores/dashboard'

vi.mock('@/api', () => ({
  fetchDashboard: vi.fn(),
}))

import { fetchDashboard } from '@/api'
const mockFetchDashboard = vi.mocked(fetchDashboard)

describe('useDashboardStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('has correct default state', () => {
    const store = useDashboardStore()
    expect(store.data).toBeNull()
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load fetches dashboard data', async () => {
    const fakeData = { total_launches: 200, total_rockets: 4 } as any
    mockFetchDashboard.mockResolvedValue(fakeData)

    const store = useDashboardStore()
    await store.load()
    expect(store.data).toEqual(fakeData)
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('load sets error on failure', async () => {
    mockFetchDashboard.mockRejectedValue(new Error('Server error'))
    const store = useDashboardStore()
    await store.load()
    expect(store.error).toBe('Failed to load dashboard')
    expect(store.data).toBeNull()
    expect(store.loading).toBe(false)
  })
})
