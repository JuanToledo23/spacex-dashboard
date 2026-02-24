import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EmissionsView from '@/views/EmissionsView.vue'

vi.mock('@/api', () => ({
  fetchEmissions: vi.fn(),
}))

import { fetchEmissions } from '@/api'
const mockFetch = vi.mocked(fetchEmissions)

const fakeEmissions = {
  total_co2_tonnes: 95000,
  total_fuel_tonnes: 120000,
  co2_per_launch: 475,
  reuse_co2_saved_tonnes: 15000,
  total_reuses: 150,
  total_launches: 200,
  emissions_by_vehicle: [
    { rocket_id: 'r1', rocket_name: 'Falcon 9', fuel_type: 'rp1', fuel_per_launch_tonnes: 475, co2_per_launch_tonnes: 458, launches: 180, total_co2_tonnes: 82000, payload_kg_leo: 22800, co2_per_kg_leo: 20.1 },
  ],
  annual_emissions: [
    { year: 2023, launches: 90, co2_tonnes: 40000, fuel_burned_tonnes: 42750, reuse_savings_tonnes: 8000 },
  ],
  fuel_breakdown: [
    { fuel_type: 'RP-1', fuel_tonnes: 100000, co2_tonnes: 85000, percentage: 83 },
  ],
}

describe('EmissionsView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))
    const wrapper = mount(EmissionsView)
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeEmissions)
  })

  it('renders emissions data after loading', async () => {
    mockFetch.mockResolvedValue(fakeEmissions as any)
    const wrapper = mount(EmissionsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Falcon 9')
    expect(wrapper.text()).toContain('200')
  })

  it('displays reuse savings', async () => {
    mockFetch.mockResolvedValue(fakeEmissions as any)
    const wrapper = mount(EmissionsView)
    await flushPromises()
    expect(wrapper.text()).toContain('150')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const wrapper = mount(EmissionsView)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })
})
