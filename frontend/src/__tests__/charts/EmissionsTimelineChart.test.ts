import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EmissionsTimelineChart from '@/components/charts/EmissionsTimelineChart.vue'

describe('EmissionsTimelineChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(EmissionsTimelineChart, {
      props: { data: [{ year: 2023, launches: 90, co2_tonnes: 40000, fuel_burned_tonnes: 42750, reuse_savings_tonnes: 8000 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has a container element', () => {
    const wrapper = mount(EmissionsTimelineChart, {
      props: { data: [{ year: 2023, launches: 90, co2_tonnes: 40000, fuel_burned_tonnes: 42750, reuse_savings_tonnes: 8000 }] },
    })
    expect(wrapper.find('.emissions-timeline').exists()).toBe(true)
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(EmissionsTimelineChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
