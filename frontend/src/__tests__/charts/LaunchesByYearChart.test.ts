import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LaunchesByYearChart from '@/components/charts/LaunchesByYearChart.vue'

describe('LaunchesByYearChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders an SVG element', () => {
    const wrapper = mount(LaunchesByYearChart, {
      props: {
        data: [{ year: 2020, total: 26, successes: 25, failures: 1 }],
      },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has chart-container with role=img', () => {
    const wrapper = mount(LaunchesByYearChart, {
      props: {
        data: [{ year: 2021, total: 31, successes: 30, failures: 1 }],
      },
    })
    const container = wrapper.find('.chart-container')
    expect(container.exists()).toBe(true)
    expect(container.attributes('role')).toBe('img')
    expect(container.attributes('aria-label')).toBeTruthy()
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(LaunchesByYearChart, {
      props: { data: [] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('renders with multiple years', () => {
    const data = [
      { year: 2020, total: 26, successes: 25, failures: 1 },
      { year: 2021, total: 31, successes: 30, failures: 1 },
      { year: 2022, total: 61, successes: 60, failures: 1 },
    ]
    const wrapper = mount(LaunchesByYearChart, {
      props: { data },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('accepts custom height prop', () => {
    const wrapper = mount(LaunchesByYearChart, {
      props: {
        data: [{ year: 2023, total: 90, successes: 88, failures: 2 }],
        height: 400,
      },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
