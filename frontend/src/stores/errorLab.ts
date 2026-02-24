import { defineStore } from 'pinia'

interface ErrorLabState {
  open: boolean
}

export const useErrorLabStore = defineStore('errorLab', {
  state: (): ErrorLabState => ({
    open: false,
  }),
  actions: {
    toggle() {
      this.open = !this.open
    },
    close() {
      this.open = false
    },
  },
})
