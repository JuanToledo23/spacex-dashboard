import { defineStore } from 'pinia'
import type { AppNotification } from '@/types'

const MAX_VISIBLE = 4
const DISMISS_MS: Record<string, number> = {
  error: 12_000,
  warning: 10_000,
  success: 8_000,
  info: 8_000,
  launch: 10_000,
}

interface NotificationState {
  notifications: AppNotification[]
}

export const useNotificationStore = defineStore('notifications', {
  state: (): NotificationState => ({
    notifications: [],
  }),
  actions: {
    add(notification: AppNotification) {
      this.notifications.push(notification)
      if (this.notifications.length > MAX_VISIBLE) {
        this.notifications.splice(0, this.notifications.length - MAX_VISIBLE)
      }

      const ms = DISMISS_MS[notification.type] ?? 8_000
      setTimeout(() => this.dismiss(notification.id), ms)
    },

    dismiss(id: string) {
      const idx = this.notifications.findIndex((n) => n.id === id)
      if (idx !== -1) this.notifications.splice(idx, 1)
    },

    connect() {
      const baseUrl = import.meta.env.DEV ? 'http://localhost:8000' : ''
      const url = `${baseUrl}/api/notifications/stream`

      const open = () => {
        const source = new EventSource(url)

        source.onmessage = (event: MessageEvent) => {
          try {
            const data = JSON.parse(event.data) as AppNotification
            if (data.id && data.type && data.title) {
              this.add(data)
            }
          } catch {
            /* ignore malformed events */
          }
        }

        source.onerror = () => {
          source.close()
          setTimeout(open, 5_000)
        }
      }

      open()
    },
  },
})
