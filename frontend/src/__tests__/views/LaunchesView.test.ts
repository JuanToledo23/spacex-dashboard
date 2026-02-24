import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import LaunchesView from '@/views/LaunchesView.vue'

vi.mock('@/api', () => ({
  fetchDashboard: vi.fn(),
  fetchRockets: vi.fn(),
  fetchLaunches: vi.fn(),
}))

import { fetchDashboard, fetchRockets, fetchLaunches } from '@/api'
const mockDash = vi.mocked(fetchDashboard)
const mockRockets = vi.mocked(fetchRockets)
const mockLaunches = vi.mocked(fetchLaunches)

const fakeDashData = {
  total_launches: 200,
  successful_launches: 195,
  success_rate: 97.5,
  launches_by_year: [],
  launches_by_rocket: [{ rocket: 'Falcon 9', count: 180 }],
  launches_by_site: [],
} as any

const fakeLaunchData = {
  items: [
    {
      id: 'l1',
      name: 'CRS-25',
      date_utc: '2024-01-10T00:00:00Z',
      success: true,
      upcoming: false,
      rocket_id: 'r1',
      rocket_name: 'Falcon 9',
      details: null,
      patch_small: null,
    },
  ],
  total: 1,
  page: 1,
  limit: 20,
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/launches', name: 'Launches', component: LaunchesView },
      { path: '/launches/:id', name: 'LaunchDetail', component: { template: '<div />' } },
    ],
  })
}

describe('LaunchesView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders page title', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockResolvedValue(fakeLaunchData as any)

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.find('.chronicle-title').text()).toBe('Launch Record')
  })

  it('shows skeleton while loading', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockImplementation(() => new Promise(() => {}))

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })

    expect(wrapper.findComponent({ name: 'SkeletonLoader' }).exists()).toBe(true)
  })

  it('renders launch data in table', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockResolvedValue(fakeLaunchData as any)

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('CRS-25')
    expect(wrapper.text()).toContain('Falcon 9')
  })

  it('renders vehicle breakdown when dashboard data available', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockResolvedValue(fakeLaunchData as any)

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('By Vehicle')
    expect(wrapper.text()).toContain('180')
  })

  it('shows error state on launches fetch failure', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockRejectedValue(new Error('fail'))

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })

  it('renders filter dropdowns', async () => {
    mockDash.mockResolvedValue(fakeDashData)
    mockRockets.mockResolvedValue([])
    mockLaunches.mockResolvedValue(fakeLaunchData as any)

    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(LaunchesView, { global: { plugins: [router] } })
    await flushPromises()

    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(2)
  })
})
