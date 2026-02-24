import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LaunchCadenceChart from '@/components/charts/LaunchCadenceChart.vue'

describe('LaunchCadenceChart', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders SVG element', () => {
    const wrapper = mount(LaunchCadenceChart, {
      props: { data: [{ year: 2023, total: 90, successes: 88, failures: 2 }] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(LaunchCadenceChart, {
      props: { data: [{ year: 2023, total: 90, successes: 88, failures: 2 }] },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
    expect(container.attributes('aria-label')).toBeTruthy()
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(LaunchCadenceChart, { props: { data: [] } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
