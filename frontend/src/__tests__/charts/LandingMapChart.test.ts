import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LandingMapChart from '@/components/charts/LandingMapChart.vue'

const mockGeoJson = { type: 'Topology', objects: { countries: { type: 'GeometryCollection', geometries: [] } }, arcs: [] }

describe('LandingMapChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGeoJson),
    } as Response)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders container element', () => {
    const wrapper = mount(LandingMapChart, {
      props: {
        landpads: [{ id: 'lp1', name: 'LZ-1', full_name: 'Landing Zone 1', type: 'RTLS', status: 'active', locality: 'Cape Canaveral', region: 'Florida', latitude: 28.4858, longitude: -80.5444, landing_attempts: 25, landing_successes: 24, success_rate: 96 }],
      },
    })
    expect(wrapper.find('.landing-map').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = mount(LandingMapChart, {
      props: {
        landpads: [{ id: 'lp1', name: 'LZ-1', full_name: 'LZ-1', type: 'RTLS', status: 'active', locality: 'Cape Canaveral', region: 'Florida', latitude: 28.4858, longitude: -80.5444, landing_attempts: 25, landing_successes: 24, success_rate: 96 }],
      },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('does not crash with empty landpads', () => {
    const wrapper = mount(LandingMapChart, { props: { landpads: [] } })
    expect(wrapper.find('.landing-map').exists()).toBe(true)
  })
})
