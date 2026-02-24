import { defineStore } from 'pinia'

type Theme = 'dark' | 'light'

interface ThemeState {
  theme: Theme
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    theme: (localStorage.getItem('theme') as Theme) || 'dark',
  }),
  actions: {
    toggle(): void {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', this.theme)
      document.documentElement.setAttribute('data-theme', this.theme)
    },
    init(): void {
      document.documentElement.setAttribute('data-theme', this.theme)
    },
  },
})
