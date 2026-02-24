import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LandingView from '@/views/LandingView.vue'

vi.mock('@/api', () => ({
  fetchLanding: vi.fn(),
}))

import { fetchLanding } from '@/api'
const mockFetch = vi.mocked(fetchLanding)

const mockGeoJson = { type: 'Topology', objects: { countries: { type: 'GeometryCollection', geometries: [] } }, arcs: [] }

const fakeLanding = {
  stats: {
    total_attempts: 270,
    total_successes: 250,
    overall_success_rate: 92.6,
    rtls_attempts: 85,
    rtls_successes: 80,
    asds_attempts: 185,
    asds_successes: 170,
  },
  landpads: [
    { id: 'lp1', name: 'LZ-1', full_name: 'Landing Zone 1', type: 'RTLS', status: 'active', locality: 'Cape Canaveral', region: 'Florida', latitude: 28.4858, longitude: -80.5444, landing_attempts: 25, landing_successes: 24, success_rate: 96 },
  ],
}

describe('LandingView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGeoJson),
    } as Response)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))
    const wrapper = mount(LandingView)
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeLanding)
  })

  it('renders landing stats after loading', async () => {
    mockFetch.mockResolvedValue(fakeLanding as any)
    const wrapper = mount(LandingView)
    await flushPromises()
    expect(wrapper.text()).toContain('250')
    expect(wrapper.text()).toContain('92.6')
  })

  it('shows RTLS and ASDS stats', async () => {
    mockFetch.mockResolvedValue(fakeLanding as any)
    const wrapper = mount(LandingView)
    await flushPromises()
    expect(wrapper.text()).toContain('RTLS')
    expect(wrapper.text()).toContain('ASDS')
  })

  it('renders landpad data', async () => {
    mockFetch.mockResolvedValue(fakeLanding as any)
    const wrapper = mount(LandingView)
    await flushPromises()
    expect(wrapper.text()).toContain('Landing Zone 1')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const wrapper = mount(LandingView)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })
})
