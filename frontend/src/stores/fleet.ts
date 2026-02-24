import { defineStore } from 'pinia'
import { fetchFleetStats, fetchRockets } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'
import type { FleetStats, RocketSummary } from '@/types'

interface FleetState {
  stats: FleetStats | null
  rockets: RocketSummary[]
  loading: boolean
  error: string | null
}

export const useFleetStore = defineStore('fleet', {
  state: (): FleetState => ({
    stats: null,
    rockets: [],
    loading: false,
    error: null,
  }),
  actions: {
    async load(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        const [stats, rockets] = await Promise.all([fetchFleetStats(), fetchRockets()])
        this.stats = stats
        this.rockets = rockets
      } catch (err) {
        this.error = extractErrorMessage(err, 'Failed to load fleet data')
      } finally {
        this.loading = false
      }
    },
  },
})
