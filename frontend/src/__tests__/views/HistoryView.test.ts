import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HistoryView from '@/views/HistoryView.vue'

vi.mock('@/api', () => ({
  fetchHistory: vi.fn(),
}))

import { fetchHistory } from '@/api'
const mockFetch = vi.mocked(fetchHistory)

const fakeHistory = {
  events: [
    { id: 'h1', title: 'Falcon 1 Success', event_date_utc: '2008-09-28T00:00:00Z', details: 'First private rocket to orbit', article: null, wikipedia: null },
    { id: 'h2', title: 'Dragon to ISS', event_date_utc: '2012-05-25T00:00:00Z', details: 'First commercial spacecraft to ISS', article: null, wikipedia: null },
  ],
  total: 2,
}

describe('HistoryView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows skeleton while loading', async () => {
    let resolve!: (_v: unknown) => void
    mockFetch.mockImplementation(() => new Promise((r) => { resolve = r }))
    const wrapper = mount(HistoryView)
    await flushPromises()
    expect(wrapper.html()).toContain('skeleton')
    resolve(fakeHistory)
  })

  it('renders history events after loading', async () => {
    mockFetch.mockResolvedValue(fakeHistory as any)
    const wrapper = mount(HistoryView)
    await flushPromises()
    expect(wrapper.text()).toContain('Falcon 1 Success')
    expect(wrapper.text()).toContain('Dragon to ISS')
  })

  it('shows error state on failure', async () => {
    mockFetch.mockRejectedValue(new Error('fail'))
    const wrapper = mount(HistoryView)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'ErrorState' }).exists()).toBe(true)
  })

  it('displays event details', async () => {
    mockFetch.mockResolvedValue(fakeHistory as any)
    const wrapper = mount(HistoryView)
    await flushPromises()
    expect(wrapper.text()).toContain('First private rocket to orbit')
  })
})
