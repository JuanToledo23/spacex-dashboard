import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AiChat from '@/components/common/AiChat.vue'

vi.mock('@/api', () => ({
  fetchAiStatus: vi.fn(),
  sendChatMessage: vi.fn(),
}))

import { fetchAiStatus, sendChatMessage } from '@/api'
const mockFetchAiStatus = vi.mocked(fetchAiStatus)
const mockSendChatMessage = vi.mocked(sendChatMessage)

describe('AiChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not render when AI is unavailable', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: false })
    const wrapper = mount(AiChat)
    await flushPromises()
    expect(wrapper.find('.ai-chat-wrapper').exists()).toBe(false)
  })

  it('renders floating button when AI is available', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    const wrapper = mount(AiChat)
    await flushPromises()
    expect(wrapper.find('.ai-fab').exists()).toBe(true)
    expect(wrapper.find('.ai-fab').attributes('aria-label')).toBe('Open AI Assistant')
  })

  it('opens chat panel when button is clicked', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    const wrapper = mount(AiChat)
    await flushPromises()

    expect(wrapper.find('.ai-panel').exists()).toBe(false)
    await wrapper.find('.ai-fab').trigger('click')
    expect(wrapper.find('.ai-panel').exists()).toBe(true)
    expect(wrapper.find('.ai-title').text()).toBe('SpaceX AI Assistant')
  })

  it('closes chat panel when close button is clicked', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    const wrapper = mount(AiChat)
    await flushPromises()

    await wrapper.find('.ai-fab').trigger('click')
    expect(wrapper.find('.ai-panel').exists()).toBe(true)

    await wrapper.find('.ai-close').trigger('click')
    expect(wrapper.find('.ai-panel').exists()).toBe(false)
  })

  it('shows welcome message in chat panel', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    const wrapper = mount(AiChat)
    await flushPromises()
    await wrapper.find('.ai-fab').trigger('click')

    const messages = wrapper.findAll('.ai-msg')
    expect(messages.length).toBe(1)
    expect(messages[0].text()).toContain('SpaceX data assistant')
  })

  it('disables send button when input is empty', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    const wrapper = mount(AiChat)
    await flushPromises()
    await wrapper.find('.ai-fab').trigger('click')

    const sendBtn = wrapper.find('.ai-send')
    expect((sendBtn.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('sends message and displays response', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    mockSendChatMessage.mockResolvedValue({ response: 'Test reply' })

    const wrapper = mount(AiChat)
    await flushPromises()
    await wrapper.find('.ai-fab').trigger('click')

    const input = wrapper.find('.ai-input')
    await input.setValue('Hello')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const userMsgs = wrapper.findAll('.ai-msg.user')
    expect(userMsgs.length).toBe(1)
    expect(userMsgs[0].text()).toBe('Hello')

    // Run typewriter timers to completion
    vi.runAllTimers()
    await flushPromises()

    const assistantMsgs = wrapper.findAll('.ai-msg.assistant')
    expect(assistantMsgs.length).toBeGreaterThanOrEqual(2)
  })

  it('handles API error gracefully', async () => {
    mockFetchAiStatus.mockResolvedValue({ available: true })
    mockSendChatMessage.mockRejectedValue(new Error('Network'))

    const wrapper = mount(AiChat)
    await flushPromises()
    await wrapper.find('.ai-fab').trigger('click')

    const input = wrapper.find('.ai-input')
    await input.setValue('Hello')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    vi.runAllTimers()
    await flushPromises()

    const allMsgs = wrapper.findAll('.ai-msg')
    expect(allMsgs.length).toBeGreaterThanOrEqual(2)
  })

  it('handles fetchAiStatus failure gracefully', async () => {
    mockFetchAiStatus.mockRejectedValue(new Error('fail'))
    const wrapper = mount(AiChat)
    await flushPromises()
    expect(wrapper.find('.ai-chat-wrapper').exists()).toBe(false)
  })
})
