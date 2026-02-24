import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from '@/components/layout/AppFooter.vue'

describe('AppFooter', () => {
  it('renders footer text', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.text()).toContain('SpaceX')
    expect(wrapper.text()).toContain('Juan Alberto Toledo Tello')
  })

  it('renders data source', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.text()).toContain('api.spacexdata.com')
  })

  it('renders as footer element', () => {
    const wrapper = mount(AppFooter)
    expect(wrapper.find('footer').exists()).toBe(true)
  })
})
