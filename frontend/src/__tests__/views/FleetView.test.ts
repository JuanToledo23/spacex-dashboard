import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import FleetView from '@/views/FleetView.vue'

vi.mock('@/api', () => ({
  fetchFleetStats: vi.fn(),
  fetchRockets: vi.fn(),
}))

import { fetchFleetStats, fetchRockets } from '@/api'
const mockStats = vi.mocked(fetchFleetStats)
const mockRockets = vi.mocked(fetchRockets)

const fakeStats = {
  total_cores: 20,
  active_cores: 10,
  retired_cores: 5,
  lost_cores: 5,
  total_landings: 250,
  total_landing_attempts: 270,
  landing_success_rate: 92.6,
  rtls_landings: 80,
  rtls_attempts: 85,
  asds_landings: 170,
  asds_attempts: 185,
  most_reused: [],
}

const fakeRockets = [
  {
    id: 'r1',
    name: 'Falcon 9',
    type: 'rocket',
    active: true,
    success_rate_pct: 98,
    launch_count: 200,
    cost_per_launch: 50000000,
    first_flight: '2010-06-04',
    description: 'Two-stage rocket',
    flickr_images: [],
    height_meters: 70,
    diameter_meters: 3.7,
    mass_kg: 549054,
  },
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/fleet', name: 'Fleet', component: FleetView },
      { path: '/rockets/:id', name: 'RocketDetail', component: { template: '<div />' } },
    ],
  })
}

describe('FleetView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolveStats!: (_v: unknown) => void
    let resolveRockets!: (_v: unknown) => void
    mockStats.mockImplementation(() => new Promise((r) => { resolveStats = r }))
    mockRockets.mockImplementation(() => new Promise((r) => { resolveRockets = r }))

    const router = makeRouter()
    await router.push('/fleet')
    await router.isReady()

    const wrapper = mount(FleetView, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('skeleton')
    resolveStats(fakeStats)
    resolveRockets(fakeRockets)
  })

  it('renders fleet stats after loading', async () => {
    mockStats.mockResolvedValue(fakeStats as any)
    mockRockets.mockResolvedValue(fakeRockets as any)

    const router = makeRouter()
    await router.push('/fleet')
    await router.isReady()

    const wrapper = mount(FleetView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('250')
    expect(wrapper.text()).toContain('92.6')
    expect(wrapper.text()).toContain('Booster Recovery')
  })

  it('shows recovery method stats', async () => {
    mockStats.mockResolvedValue(fakeStats as any)
    mockRockets.mockResolvedValue(fakeRockets as any)

    const router = makeRouter()
    await router.push('/fleet')
    await router.isReady()

    const wrapper = mount(FleetView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('RTLS Landings')
    expect(wrapper.text()).toContain('80')
    expect(wrapper.text()).toContain('ASDS Landings')
    expect(wrapper.text()).toContain('170')
    expect(wrapper.text()).toContain('Active Boosters')
    expect(wrapper.text()).toContain('10')
  })

  it('renders rocket showcase cards', async () => {
    mockStats.mockResolvedValue(fakeStats as any)
    mockRockets.mockResolvedValue(fakeRockets as any)

    const router = makeRouter()
    await router.push('/fleet')
    await router.isReady()

    const wrapper = mount(FleetView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Falcon 9')
    expect(wrapper.text()).toContain('200')
    expect(wrapper.text()).toContain('98%')
    expect(wrapper.text()).toContain('$50M')
  })

  it('shows error state on failure', async () => {
    mockStats.mockRejectedValue(new Error('fail'))
    mockRockets.mockRejectedValue(new Error('fail'))

    const router = makeRouter()
    await router.push('/fleet')
    await router.isReady()

    const wrapper = mount(FleetView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })
})
