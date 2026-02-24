import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationStore } from '@/stores/notifications'

describe('useNotificationStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('has correct default state', () => {
    const store = useNotificationStore()
    expect(store.notifications).toEqual([])
  })

  it('adds a notification', () => {
    const store = useNotificationStore()
    store.add({
      id: '1',
      type: 'success',
      title: 'Done',
      message: 'All good',
      timestamp: '2025-01-01T00:00:00Z',
    })
    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0].title).toBe('Done')
    vi.useRealTimers()
  })

  it('dismisses a notification by id', () => {
    const store = useNotificationStore()
    store.add({
      id: 'x',
      type: 'info',
      title: 'T',
      message: 'M',
      timestamp: '',
    })
    expect(store.notifications).toHaveLength(1)
    store.dismiss('x')
    expect(store.notifications).toHaveLength(0)
    vi.useRealTimers()
  })

  it('auto-dismisses after timeout', () => {
    const store = useNotificationStore()
    store.add({
      id: 'auto',
      type: 'success',
      title: 'T',
      message: 'M',
      timestamp: '',
    })
    expect(store.notifications).toHaveLength(1)
    vi.advanceTimersByTime(9000)
    expect(store.notifications).toHaveLength(0)
    vi.useRealTimers()
  })

  it('limits to 4 visible notifications', () => {
    const store = useNotificationStore()
    for (let i = 0; i < 6; i++) {
      store.add({
        id: String(i),
        type: 'info',
        title: `T${i}`,
        message: `M${i}`,
        timestamp: '',
      })
    }
    expect(store.notifications.length).toBeLessThanOrEqual(4)
    vi.useRealTimers()
  })

  it('dismiss with unknown id is a no-op', () => {
    const store = useNotificationStore()
    store.add({
      id: 'a',
      type: 'info',
      title: 'T',
      message: 'M',
      timestamp: '',
    })
    store.dismiss('nonexistent')
    expect(store.notifications).toHaveLength(1)
    vi.useRealTimers()
  })
})
