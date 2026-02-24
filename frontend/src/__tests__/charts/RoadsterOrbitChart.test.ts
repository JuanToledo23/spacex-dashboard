import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RoadsterOrbitChart from '@/components/charts/RoadsterOrbitChart.vue'

describe('RoadsterOrbitChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(RoadsterOrbitChart, {
      props: { apoapsis: 1.664, periapsis: 0.986, semiMajorAxis: 1.325 },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has container element', () => {
    const wrapper = mount(RoadsterOrbitChart, {
      props: { apoapsis: 1.664, periapsis: 0.986, semiMajorAxis: 1.325 },
    })
    expect(wrapper.find('.orbit-chart').exists()).toBe(true)
  })

  it('renders without props (defaults)', () => {
    const wrapper = mount(RoadsterOrbitChart)
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
