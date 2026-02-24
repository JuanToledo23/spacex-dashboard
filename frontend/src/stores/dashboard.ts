import { defineStore } from 'pinia'
import { fetchDashboard } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'
import type { DashboardResponse } from '@/types'

interface DashboardState {
  data: DashboardResponse | null
  loading: boolean
  error: string | null
}

export const useDashboardStore = defineStore('dashboard', {
  state: (): DashboardState => ({
    data: null,
    loading: false,
    error: null,
  }),
  actions: {
    async load(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        this.data = await fetchDashboard()
      } catch (err) {
        this.error = extractErrorMessage(err, 'Failed to load dashboard')
      } finally {
        this.loading = false
      }
    },
  },
})
