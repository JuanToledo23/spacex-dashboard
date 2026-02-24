import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import LaunchDetailView from '@/views/LaunchDetailView.vue'

vi.mock('@/api', () => ({
  fetchLaunchDetail: vi.fn(),
}))

import { fetchLaunchDetail } from '@/api'
const mockFetch = vi.mocked(fetchLaunchDetail)

const fakeLaunch = {
  id: 'abc123',
  flight_number: 150,
  name: 'CRS-25',
  date_utc: '2024-01-10T00:00:00.000Z',
  success: true,
  upcoming: false,
  details: 'Cargo resupply mission to ISS',
  rocket_id: 'r1',
  rocket_name: 'Falcon 9',
  launchpad_name: 'KSC LC-39A',
  cores: [{ serial: 'B1060', flight: 15, reused: true, landing_attempt: true, landing_success: true, landing_type: 'ASDS' }],
  payloads: [{ id: 'p1', name: 'Dragon CRS-25', type: 'Dragon 2.0', customers: ['NASA'], mass_kg: 3000, orbit: 'ISS', regime: 'low-earth' }],
  crew: [],
  links: { webcast: 'https://youtube.com/watch', article: null, wikipedia: null, presskit: null, reddit_campaign: null, flickr_original: [], patch_small: null, patch_large: null },
  failures: [],
  fairings_recovered: null,
  fairings_reused: null,
  static_fire_date_utc: '2024-01-05T00:00:00Z',
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/launches/:id', name: 'LaunchDetail', component: LaunchDetailView },
    ],
  })
}

describe('LaunchDetailView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    const wrapper = mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeLaunch)
  })

  it('renders launch detail after loading', async () => {
    mockFetch.mockResolvedValue(fakeLaunch as any)

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    const wrapper = mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('CRS-25')
    expect(wrapper.text()).toContain('Falcon 9')
    expect(wrapper.text()).toContain('Cargo resupply mission to ISS')
  })

  it('displays core info', async () => {
    mockFetch.mockResolvedValue(fakeLaunch as any)

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    const wrapper = mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('B1060')
  })

  it('displays payload info', async () => {
    mockFetch.mockResolvedValue(fakeLaunch as any)

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    const wrapper = mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Dragon CRS-25')
    expect(wrapper.text()).toContain('NASA')
  })

  it('shows error on failure', async () => {
    mockFetch.mockRejectedValue(new Error('Not found'))

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    const wrapper = mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load launch')
  })

  it('fetches with route param id', async () => {
    mockFetch.mockResolvedValue(fakeLaunch as any)

    const router = makeRouter()
    await router.push('/launches/abc123')
    await router.isReady()

    mount(LaunchDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(mockFetch).toHaveBeenCalledWith('abc123')
  })
})
