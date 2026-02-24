import { defineStore } from 'pinia'
import { fetchLaunches } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'
import type { LaunchSummary, LaunchQueryParams } from '@/types'

interface LaunchFilters {
  success: boolean | null
  upcoming: boolean | null
  rocket_id: string | null
}

interface LaunchesState {
  items: LaunchSummary[]
  total: number
  page: number
  limit: number
  loading: boolean
  error: string | null
  filters: LaunchFilters
}

export const useLaunchesStore = defineStore('launches', {
  state: (): LaunchesState => ({
    items: [],
    total: 0,
    page: 1,
    limit: 20,
    loading: false,
    error: null,
    filters: {
      success: null,
      upcoming: null,
      rocket_id: null,
    },
  }),
  actions: {
    async load(params: LaunchQueryParams = {}): Promise<void> {
      this.loading = true
      this.error = null
      try {
        const query: Record<string, string | number | boolean> = {
          page: this.page,
          limit: this.limit,
        }
        const merged = { ...this.filters, ...params }
        for (const [key, val] of Object.entries(merged)) {
          if (val !== null && val !== undefined) {
            query[key] = val
          }
        }
        const data = await fetchLaunches(query as LaunchQueryParams)
        this.items = data.items
        this.total = data.total
        this.page = data.page
      } catch (err) {
        this.error = extractErrorMessage(err, 'Failed to load launches')
      } finally {
        this.loading = false
      }
    },
    setPage(page: number): void {
      this.page = page
      this.load()
    },
    setFilters(filters: Partial<LaunchFilters>): void {
      this.filters = { ...this.filters, ...filters }
      this.page = 1
      this.load()
    },
  },
})
