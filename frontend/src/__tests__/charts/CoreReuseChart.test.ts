import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CoreReuseChart from '@/components/charts/CoreReuseChart.vue'

const fakeCores = [
  {
    id: 'c1',
    serial: 'B1060',
    status: 'active',
    reuse_count: 19,
    rtls_landings: 5,
    rtls_attempts: 5,
    asds_landings: 14,
    asds_attempts: 14,
    total_landings: 19,
    total_attempts: 19,
    launches: 20,
  },
  {
    id: 'c2',
    serial: 'B1061',
    status: 'active',
    reuse_count: 16,
    rtls_landings: 4,
    rtls_attempts: 4,
    asds_landings: 12,
    asds_attempts: 12,
    total_landings: 16,
    total_attempts: 16,
    launches: 17,
  },
]

describe('CoreReuseChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders SVG element', () => {
    const wrapper = mount(CoreReuseChart, {
      props: { data: fakeCores as any },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has accessible container', () => {
    const wrapper = mount(CoreReuseChart, {
      props: { data: fakeCores as any },
    })
    const container = wrapper.find('.chart-container')
    expect(container.attributes('role')).toBe('img')
    expect(container.attributes('aria-label')).toBe('Booster reuse leaderboard')
  })

  it('does not crash with empty data', () => {
    const wrapper = mount(CoreReuseChart, {
      props: { data: [] },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
