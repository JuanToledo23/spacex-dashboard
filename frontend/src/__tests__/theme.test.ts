import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useThemeStore } from '@/stores/theme'

describe('useThemeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
  })

  it('defaults to dark theme', () => {
    const store = useThemeStore()
    expect(store.theme).toBe('dark')
  })

  it('reads saved theme from localStorage', () => {
    localStorage.setItem('theme', 'light')
    setActivePinia(createPinia())
    const store = useThemeStore()
    expect(store.theme).toBe('light')
  })

  it('toggle switches dark to light', () => {
    const store = useThemeStore()
    store.toggle()
    expect(store.theme).toBe('light')
    expect(localStorage.getItem('theme')).toBe('light')
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('toggle switches light to dark', () => {
    const store = useThemeStore()
    store.toggle()
    store.toggle()
    expect(store.theme).toBe('dark')
  })

  it('init sets data-theme attribute', () => {
    const store = useThemeStore()
    store.init()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
