import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorState from '@/components/common/ErrorState.vue'

describe('ErrorState', () => {
  it('renders default message', () => {
    const wrapper = mount(ErrorState)
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('renders custom message', () => {
    const wrapper = mount(ErrorState, { props: { message: 'Custom error' } })
    expect(wrapper.text()).toContain('Custom error')
  })

  it('shows ERROR label', () => {
    const wrapper = mount(ErrorState)
    expect(wrapper.find('.error-label').text()).toBe('ERROR')
  })

  it('emits retry on button click', async () => {
    const wrapper = mount(ErrorState)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })

  it('has retry button with text RETRY', () => {
    const wrapper = mount(ErrorState)
    expect(wrapper.find('button').text()).toBe('RETRY')
  })
})
