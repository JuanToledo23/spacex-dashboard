import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RocketSuccessChart from '@/components/charts/RocketSuccessChart.vue'

const fakeRockets = [
  {
    id: 'r1',
    name: 'Falcon 9',
    type: 'rocket',
    active: true,
    success_rate_pct: 98,
    launch_count: 200,
    flickr_images: [],
  },
  {
    id: 'r2',
    name: 'Falcon Heavy',
    type: 'rocket',
    active: true,
    success_rate_pct: 100,
    launch_count: 7,
    flickr_images: [],
  },
]

describe('RocketSuccessChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders SVG element', () => {
    const wrapper = mount(RocketSuccessChart, {
      props: { data: fakeRockets as any },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(RocketSuccessChart, {
      props: { data: fakeRockets as any },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
    expect(container.attributes('aria-label')).toBe('Rocket success rates')
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(RocketSuccessChart, {
      props: { data: [] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
