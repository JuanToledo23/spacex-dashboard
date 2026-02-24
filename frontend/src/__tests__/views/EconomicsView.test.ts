import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EconomicsView from '@/views/EconomicsView.vue'

vi.mock('@/api', () => ({
  fetchEconomics: vi.fn(),
}))

import { fetchEconomics } from '@/api'
const mockFetch = vi.mocked(fetchEconomics)

const fakeEconomics = {
  total_estimated_spend: 15000000000,
  total_launches: 200,
  total_payloads: 350,
  total_mass_launched_kg: 500000,
  avg_cost_per_launch: 75000000,
  lowest_cost_per_kg: 2720,
  lowest_cost_vehicle: 'Falcon 9',
  cost_by_vehicle: [
    { rocket_id: 'r1', rocket_name: 'Falcon 9', cost_per_launch: 50000000, launches: 180, total_spend: 9000000000, payload_kg_leo: 22800, cost_per_kg_leo: 2193 },
  ],
  annual_spend: [
    { year: 2023, launches: 90, total_spend: 4500000000, avg_cost: 50000000 },
  ],
  top_customers: [
    { customer: 'SpaceX', payloads: 150, total_mass_kg: 200000 },
  ],
  mass_by_orbit: [
    { orbit: 'LEO', total_mass_kg: 300000, payloads: 200 },
  ],
}

describe('EconomicsView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))
    const wrapper = mount(EconomicsView)
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeEconomics)
  })

  it('renders economics data after loading', async () => {
    mockFetch.mockResolvedValue(fakeEconomics as any)
    const wrapper = mount(EconomicsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Falcon 9')
    expect(wrapper.text()).toContain('200')
  })

  it('displays cost by vehicle section', async () => {
    mockFetch.mockResolvedValue(fakeEconomics as any)
    const wrapper = mount(EconomicsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Falcon 9')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const wrapper = mount(EconomicsView)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })

  it('displays top customers', async () => {
    mockFetch.mockResolvedValue(fakeEconomics as any)
    const wrapper = mount(EconomicsView)
    await flushPromises()
    expect(wrapper.text()).toContain('SpaceX')
  })
})
