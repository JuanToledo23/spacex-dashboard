import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import StarlinkView from '@/views/StarlinkView.vue'

vi.mock('@/api', () => ({
  fetchStarlink: vi.fn(),
  fetchStarlinkStats: vi.fn(),
  fetchStarlinkPositions: vi.fn(),
}))

import { fetchStarlink, fetchStarlinkStats, fetchStarlinkPositions } from '@/api'
const mockFetchList = vi.mocked(fetchStarlink)
const mockFetchStats = vi.mocked(fetchStarlinkStats)
const mockFetchPositions = vi.mocked(fetchStarlinkPositions)

const mockGeoJson = { type: 'Topology', objects: { countries: { type: 'GeometryCollection', geometries: [] } }, arcs: [] }

const fakeStats = {
  total: 5000,
  by_version: [
    { version: 'v1.5', count: 3000 },
    { version: 'v2.0', count: 2000 },
  ],
  avg_height_km: 550,
}

const fakePositions = [
  { id: 's1', object_name: 'STARLINK-1234', latitude: 40, longitude: -73, height_km: 550, velocity_kms: 7.6, version: 'v1.5' },
]

const fakeList = {
  items: [
    { id: 's1', object_name: 'STARLINK-1234', version: 'v1.5', height_km: 550, latitude: 40, longitude: -73, velocity_kms: 7.6, launch_id: null },
  ],
  total: 1,
  page: 1,
  limit: 20,
}

function mockCanvasContext() {
  return {
    clearRect: () => {}, fillRect: () => {}, fillStyle: '', strokeStyle: '',
    lineWidth: 0, globalAlpha: 1, beginPath: () => {}, arc: () => {},
    fill: () => {}, stroke: () => {}, moveTo: () => {}, lineTo: () => {},
    closePath: () => {}, save: () => {}, restore: () => {}, scale: () => {},
    setTransform: () => {}, translate: () => {}, rotate: () => {}, clip: () => {},
    measureText: () => ({ width: 0 }), fillText: () => {},
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createRadialGradient: () => ({ addColorStop: () => {} }),
    canvas: { width: 800, height: 600 },
  }
}

describe('StarlinkView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    HTMLCanvasElement.prototype.getContext = () => mockCanvasContext() as any
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGeoJson),
    } as Response)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows skeleton while loading', async () => {
    mockFetchList.mockImplementation(() => new Promise(() => {}))
    mockFetchStats.mockImplementation(() => new Promise(() => {}))
    mockFetchPositions.mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(StarlinkView)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('skeleton')
  })

  it('renders starlink data after loading', async () => {
    mockFetchList.mockResolvedValue(fakeList as any)
    mockFetchStats.mockResolvedValue(fakeStats as any)
    mockFetchPositions.mockResolvedValue(fakePositions as any)

    const wrapper = mount(StarlinkView)
    await flushPromises()

    expect(wrapper.text()).toContain('5,000')
    expect(wrapper.text()).toContain('550')
  })

  it('displays version breakdown', async () => {
    mockFetchList.mockResolvedValue(fakeList as any)
    mockFetchStats.mockResolvedValue(fakeStats as any)
    mockFetchPositions.mockResolvedValue(fakePositions as any)

    const wrapper = mount(StarlinkView)
    await flushPromises()

    expect(wrapper.text()).toContain('v1.5')
    expect(wrapper.text()).toContain('v2.0')
  })

  it('shows error state on failure', async () => {
    mockFetchList.mockRejectedValue(new Error('fail'))
    mockFetchStats.mockResolvedValue(fakeStats as any)
    mockFetchPositions.mockResolvedValue(fakePositions as any)

    const wrapper = mount(StarlinkView)
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })
})
