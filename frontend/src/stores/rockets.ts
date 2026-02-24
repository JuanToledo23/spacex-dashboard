import { defineStore } from 'pinia'
import { fetchRockets } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'
import type { RocketSummary } from '@/types'

interface RocketsState {
  items: RocketSummary[]
  loading: boolean
  error: string | null
}

export const useRocketsStore = defineStore('rockets', {
  state: (): RocketsState => ({
    items: [],
    loading: false,
    error: null,
  }),
  actions: {
    async load(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        this.items = await fetchRockets()
      } catch (err) {
        this.error = extractErrorMessage(err, 'Failed to load rockets')
      } finally {
        this.loading = false
      }
    },
  },
})
