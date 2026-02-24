import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import RocketDetailView from '@/views/RocketDetailView.vue'

vi.mock('@/api', () => ({
  fetchRocketDetail: vi.fn(),
}))

import { fetchRocketDetail } from '@/api'
const mockFetch = vi.mocked(fetchRocketDetail)

const fakeRocket = {
  id: 'r1',
  name: 'Falcon 9',
  type: 'rocket',
  active: true,
  stages: 2,
  boosters: 0,
  cost_per_launch: 50000000,
  success_rate_pct: 98.2,
  first_flight: '2010-06-04',
  country: 'United States',
  description: 'Falcon 9 is a two-stage rocket',
  wikipedia: 'https://en.wikipedia.org/wiki/Falcon_9',
  flickr_images: ['https://example.com/f9.jpg'],
  height_meters: 70,
  diameter_meters: 3.7,
  mass_kg: 549054,
  engines: { number: 9, type: 'merlin', version: '1D+', propellant_1: 'liquid oxygen', propellant_2: 'RP-1', thrust_sea_level_kn: 7607, thrust_vacuum_kn: 8227, isp_sea_level: 282, isp_vacuum: 311, thrust_to_weight: 180.1 },
  payload_weights: [{ id: 'leo', name: 'Low Earth Orbit', kg: 22800, lb: 50265 }],
  first_stage: { reusable: true, engines: 9, fuel_amount_tons: 385, burn_time_sec: 162, thrust_sea_level_kn: 7607, thrust_vacuum_kn: 8227 },
  second_stage: { reusable: false, engines: 1, fuel_amount_tons: 90, burn_time_sec: 397, thrust_sea_level_kn: null, thrust_vacuum_kn: 934 },
  landing_legs_number: 4,
  landing_legs_material: 'carbon fiber',
  launch_count: 200,
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/rockets/:id', name: 'RocketDetail', component: RocketDetailView },
    ],
  })
}

describe('RocketDetailView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    const wrapper = mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeRocket)
  })

  it('renders rocket detail after loading', async () => {
    mockFetch.mockResolvedValue(fakeRocket as any)

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    const wrapper = mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Falcon 9')
    expect(wrapper.text()).toContain('98.2')
    expect(wrapper.text()).toContain('200')
  })

  it('displays engine specs', async () => {
    mockFetch.mockResolvedValue(fakeRocket as any)

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    const wrapper = mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('merlin')
  })

  it('displays payload capacity', async () => {
    mockFetch.mockResolvedValue(fakeRocket as any)

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    const wrapper = mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('22,800')
  })

  it('shows error on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    const wrapper = mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load rocket')
  })

  it('fetches with route param id', async () => {
    mockFetch.mockResolvedValue(fakeRocket as any)

    const router = makeRouter()
    await router.push('/rockets/r1')
    await router.isReady()

    mount(RocketDetailView, { global: { plugins: [router] } })
    await flushPromises()

    expect(mockFetch).toHaveBeenCalledWith('r1')
  })
})
