import { defineStore } from 'pinia'
import { fetchStarlink } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'
import type { StarlinkSatellite, StarlinkQueryParams } from '@/types'

interface StarlinkState {
  items: StarlinkSatellite[]
  total: number
  page: number
  limit: number
  loading: boolean
  error: string | null
  version: string | null
}

export const useStarlinkStore = defineStore('starlink', {
  state: (): StarlinkState => ({
    items: [],
    total: 0,
    page: 1,
    limit: 20,
    loading: false,
    error: null,
    version: null,
  }),
  actions: {
    async load(params: StarlinkQueryParams = {}): Promise<void> {
      this.loading = true
      this.error = null
      try {
        const query: StarlinkQueryParams = {
          page: this.page,
          limit: this.limit,
          ...params,
        }
        if (this.version) query.version = this.version
        const data = await fetchStarlink(query)
        this.items = data.items
        this.total = data.total
        this.page = data.page
      } catch (err) {
        this.error = extractErrorMessage(err, 'Failed to load starlink data')
      } finally {
        this.loading = false
      }
    },
    setPage(page: number): void {
      this.page = page
      this.load()
    },
    setVersion(version: string | null): void {
      this.version = version
      this.page = 1
      this.load()
    },
  },
})
