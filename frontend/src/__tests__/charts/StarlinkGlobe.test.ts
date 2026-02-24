import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import StarlinkGlobe from '@/components/charts/StarlinkGlobe.vue'

const mockGeoJson = { type: 'Topology', objects: { countries: { type: 'GeometryCollection', geometries: [] } }, arcs: [] }

function mockCanvasContext() {
  return {
    clearRect: () => {},
    fillRect: () => {},
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    globalAlpha: 1,
    beginPath: () => {},
    arc: () => {},
    fill: () => {},
    stroke: () => {},
    moveTo: () => {},
    lineTo: () => {},
    closePath: () => {},
    save: () => {},
    restore: () => {},
    scale: () => {},
    setTransform: () => {},
    translate: () => {},
    rotate: () => {},
    clip: () => {},
    measureText: () => ({ width: 0 }),
    fillText: () => {},
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createRadialGradient: () => ({ addColorStop: () => {} }),
    canvas: { width: 800, height: 600 },
  }
}

describe('StarlinkGlobe', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    HTMLCanvasElement.prototype.getContext = () => mockCanvasContext() as any
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGeoJson),
    } as Response)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders container element', () => {
    const wrapper = mount(StarlinkGlobe, {
      props: {
        positions: [{ id: 's1', object_name: 'SAT-1', latitude: 40, longitude: -73, height_km: 550, velocity_kms: 7.6, version: 'v1.5' }],
        activeVersions: new Set(['v1.5']),
        selectedSat: null,
        versionColorMap: { 'v1.5': '#22c55e' },
      },
    })
    expect(wrapper.find('.globe-container').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(StarlinkGlobe, {
      props: {
        positions: [],
        activeVersions: new Set(),
        selectedSat: null,
        versionColorMap: {},
      },
    })
    const container = wrapper.find('.globe-container')
    expect(container.attributes('role')).toBe('img')
  })

  it('does not crash with empty positions', () => {
    const wrapper = mount(StarlinkGlobe, {
      props: {
        positions: [],
        activeVersions: new Set(),
        selectedSat: null,
        versionColorMap: {},
      },
    })
    expect(wrapper.find('.globe-container').exists()).toBe(true)
  })
})
