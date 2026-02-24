import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MassByOrbitChart from '@/components/charts/MassByOrbitChart.vue'

describe('MassByOrbitChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(MassByOrbitChart, {
      props: { data: [{ orbit: 'LEO', total_mass_kg: 300000, payloads: 200 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(MassByOrbitChart, {
      props: { data: [{ orbit: 'LEO', total_mass_kg: 300000, payloads: 200 }] },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(MassByOrbitChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
