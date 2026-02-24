import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import OverviewView from '@/views/OverviewView.vue'

vi.mock('@/api', () => ({
  fetchDashboard: vi.fn(),
}))

import { fetchDashboard } from '@/api'
const mockFetch = vi.mocked(fetchDashboard)

const fakeDashboard = {
  total_rockets: 4,
  active_rockets: 2,
  total_launches: 205,
  successful_launches: 200,
  failed_launches: 3,
  upcoming_launches: 2,
  success_rate: 98.5,
  launches_by_year: [{ year: 2023, total: 60, successes: 59, failures: 1 }],
  launches_by_rocket: [{ rocket: 'Falcon 9', count: 180 }],
  launches_by_site: [{ site: 'KSC LC-39A', count: 100 }],
  total_starlink: 5000,
  active_cores: 10,
  total_landings: 250,
  latest_launch: {
    id: 'l1',
    name: 'Starlink 6-30',
    date_utc: '2024-01-15T00:00:00Z',
    success: true,
    upcoming: false,
    rocket_name: 'Falcon 9',
    details: null,
    patch_small: null,
    webcast: null,
    flickr_images: [],
  },
  next_launch: null,
  recent_launches: [],
  insights: [{ id: 'i1', type: 'metric', text: 'Test insight', payload: null }],
  launchpads: [],
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', name: 'Overview', component: OverviewView }],
  })
}

describe('OverviewView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows skeleton loaders while loading', async () => {
    let resolvePromise!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolvePromise = r }))
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('skeleton')
    resolvePromise(fakeDashboard)
  })

  it('renders dashboard data after loading', async () => {
    mockFetch.mockResolvedValue(fakeDashboard as any)
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('205')
    expect(wrapper.text()).toContain('98.5')
    expect(wrapper.text()).toContain('250')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })

  it('displays insights section', async () => {
    mockFetch.mockResolvedValue(fakeDashboard as any)
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Test insight')
    expect(wrapper.text()).toContain('Recommended Actions')
  })

  it('displays latest mission info', async () => {
    mockFetch.mockResolvedValue(fakeDashboard as any)
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Starlink 6-30')
    expect(wrapper.text()).toContain('Latest Mission')
  })

  it('displays stat cells with correct values', async () => {
    mockFetch.mockResolvedValue(fakeDashboard as any)
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(OverviewView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    const stats = wrapper.findAll('.stat-cell')
    expect(stats.length).toBe(3)
    expect(stats[0].text()).toContain('Missions')
    expect(stats[1].text()).toContain('Success Rate')
    expect(stats[2].text()).toContain('Booster Landings')
  })
})
