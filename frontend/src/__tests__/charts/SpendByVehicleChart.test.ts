import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SpendByVehicleChart from '@/components/charts/SpendByVehicleChart.vue'

describe('SpendByVehicleChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(SpendByVehicleChart, {
      props: { data: [{ rocket_id: 'r1', rocket_name: 'Falcon 9', cost_per_launch: 50000000, launches: 180, total_spend: 9000000000, payload_kg_leo: 22800, cost_per_kg_leo: 2193 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(SpendByVehicleChart, {
      props: { data: [{ rocket_id: 'r1', rocket_name: 'F9', cost_per_launch: 50000000, launches: 1, total_spend: 50000000 }] },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(SpendByVehicleChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
