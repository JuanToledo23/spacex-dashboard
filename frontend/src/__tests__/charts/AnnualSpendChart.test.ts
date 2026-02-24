import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AnnualSpendChart from '@/components/charts/AnnualSpendChart.vue'

describe('AnnualSpendChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(AnnualSpendChart, {
      props: { data: [{ year: 2023, launches: 90, total_spend: 4500000000, avg_cost: 50000000 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(AnnualSpendChart, {
      props: { data: [{ year: 2023, launches: 90, total_spend: 4500000000, avg_cost: 50000000 }] },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
    expect(container.attributes('aria-label')).toBeTruthy()
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(AnnualSpendChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
