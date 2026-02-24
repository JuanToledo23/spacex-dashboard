import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FuelBreakdownChart from '@/components/charts/FuelBreakdownChart.vue'

describe('FuelBreakdownChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(FuelBreakdownChart, {
      props: { data: [{ fuel_type: 'RP-1', fuel_tonnes: 100000, co2_tonnes: 85000, percentage: 83 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has a container element', () => {
    const wrapper = mount(FuelBreakdownChart, {
      props: { data: [{ fuel_type: 'RP-1', fuel_tonnes: 100000, co2_tonnes: 85000, percentage: 83 }] },
    })
    expect(wrapper.find('.fuel-breakdown').exists()).toBe(true)
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(FuelBreakdownChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
