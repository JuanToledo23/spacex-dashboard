import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import NotificationToast from '@/components/common/NotificationToast.vue'
import { useNotificationStore } from '@/stores/notifications'

describe('NotificationToast', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('renders nothing when no notifications', () => {
    const wrapper = mount(NotificationToast)
    expect(wrapper.findAll('.notif-toast')).toHaveLength(0)
    vi.useRealTimers()
  })

  it('renders a notification toast', () => {
    const store = useNotificationStore()
    store.add({
      id: 'n1',
      type: 'launch',
      title: 'Falcon 9 Liftoff',
      message: 'Starlink mission',
      timestamp: '2025-01-01T00:00:00Z',
    })

    const wrapper = mount(NotificationToast)
    expect(wrapper.findAll('.notif-toast')).toHaveLength(1)
    expect(wrapper.text()).toContain('Falcon 9 Liftoff')
    expect(wrapper.text()).toContain('Starlink mission')
    vi.useRealTimers()
  })

  it('applies correct type class', () => {
    const store = useNotificationStore()
    store.add({
      id: 'n2',
      type: 'error',
      title: 'Failure',
      message: 'Something went wrong',
      timestamp: '',
    })

    const wrapper = mount(NotificationToast)
    expect(wrapper.find('.notif-error').exists()).toBe(true)
    vi.useRealTimers()
  })

  it('dismiss button removes notification', async () => {
    const store = useNotificationStore()
    store.add({
      id: 'n3',
      type: 'success',
      title: 'OK',
      message: 'Done',
      timestamp: '',
    })

    const wrapper = mount(NotificationToast)
    expect(wrapper.findAll('.notif-toast')).toHaveLength(1)
    await wrapper.find('.notif-close').trigger('click')
    expect(store.notifications).toHaveLength(0)
    vi.useRealTimers()
  })
})
