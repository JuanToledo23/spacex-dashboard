import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import FunFact from '@/components/common/FunFact.vue'

vi.mock('@/api', () => ({
  fetchFunFact: vi.fn(),
}))

import { fetchFunFact } from '@/api'
const mockFetchFunFact = vi.mocked(fetchFunFact)

describe('FunFact', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  it('shows fun fact when API returns data', async () => {
    mockFetchFunFact.mockResolvedValue({ fact: 'SpaceX has landed 200+ boosters' })
    const wrapper = mount(FunFact)
    await flushPromises()
    expect(wrapper.text()).toContain('SpaceX has landed 200+ boosters')
    expect(wrapper.text()).toContain('Did you know?')
    vi.useRealTimers()
  })

  it('stays hidden when API fails', async () => {
    mockFetchFunFact.mockRejectedValue(new Error('fail'))
    const wrapper = mount(FunFact)
    await flushPromises()
    expect(wrapper.find('.funfact-bar').exists()).toBe(false)
    vi.useRealTimers()
  })

  it('stays hidden when fact is empty', async () => {
    mockFetchFunFact.mockResolvedValue({ fact: '' })
    const wrapper = mount(FunFact)
    await flushPromises()
    expect(wrapper.find('.funfact-bar').exists()).toBe(false)
    vi.useRealTimers()
  })

  it('dismiss hides the fact', async () => {
    mockFetchFunFact.mockResolvedValue({ fact: 'Cool fact' })
    const wrapper = mount(FunFact)
    await flushPromises()
    expect(wrapper.find('.funfact-bar').exists()).toBe(true)
    await wrapper.find('.funfact-close').trigger('click')
    expect(wrapper.find('.funfact-bar').exists()).toBe(false)
    vi.useRealTimers()
  })

  it('auto-dismisses after duration', async () => {
    mockFetchFunFact.mockResolvedValue({ fact: 'Timed fact' })
    const wrapper = mount(FunFact)
    await flushPromises()
    expect(wrapper.find('.funfact-bar').exists()).toBe(true)
    vi.advanceTimersByTime(13000)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.funfact-bar').exists()).toBe(false)
    vi.useRealTimers()
  })
})
