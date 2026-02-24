import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import StarmanView from '@/views/StarmanView.vue'

vi.mock('@/api', () => ({
  fetchRoadster: vi.fn(),
}))

import { fetchRoadster } from '@/api'
const mockFetch = vi.mocked(fetchRoadster)

const fakeRoadster = {
  name: 'Elon Musk\'s Tesla Roadster',
  launch_date_utc: '2018-02-06T20:45:00.000Z',
  speed_kph: 75000,
  earth_distance_km: 300000000,
  earth_distance_mi: 186000000,
  mars_distance_km: 150000000,
  mars_distance_mi: 93000000,
  orbit_type: 'heliocentric',
  period_days: 557,
  apoapsis_au: 1.664,
  periapsis_au: 0.986,
  semi_major_axis_au: 1.325,
  eccentricity: 0.256,
  inclination: 1.078,
  details: 'A cherry red Tesla Roadster',
  wikipedia: 'https://en.wikipedia.org/wiki/Elon_Musk%27s_Tesla_Roadster',
  video: 'https://youtu.be/wbSwFU6tY1c',
  flickr_images: ['https://example.com/roadster.jpg'],
}

describe('StarmanView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))
    const wrapper = mount(StarmanView)
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeRoadster)
  })

  it('renders roadster data after loading', async () => {
    mockFetch.mockResolvedValue(fakeRoadster as any)
    const wrapper = mount(StarmanView)
    await flushPromises()
    expect(wrapper.text()).toContain('Tesla Roadster')
    expect(wrapper.text()).toContain('heliocentric')
  })

  it('displays orbital parameters', async () => {
    mockFetch.mockResolvedValue(fakeRoadster as any)
    const wrapper = mount(StarmanView)
    await flushPromises()
    expect(wrapper.text()).toContain('557')
    expect(wrapper.text()).toContain('1.664')
    expect(wrapper.text()).toContain('0.986')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const wrapper = mount(StarmanView)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })
})
