import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Overview', component: { template: '<div />' } },
      { path: '/launches', name: 'Launches', component: { template: '<div />' } },
      { path: '/fleet', name: 'Fleet', component: { template: '<div />' } },
      { path: '/starlink', name: 'Starlink', component: { template: '<div />' } },
      { path: '/economics', name: 'Economics', component: { template: '<div />' } },
      { path: '/emissions', name: 'Emissions', component: { template: '<div />' } },
      { path: '/history', name: 'History', component: { template: '<div />' } },
      { path: '/landing', name: 'Landing', component: { template: '<div />' } },
      { path: '/starman', name: 'Starman', component: { template: '<div />' } },
    ],
  })
}

describe('AppHeader', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the brand link', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.topbar-brand').exists()).toBe(true)
    expect(wrapper.text()).toContain('SPACEX')
  })

  it('renders desktop navigation links', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const navLinks = wrapper.findAll('.desktop-nav .nav-link')
    expect(navLinks.length).toBeGreaterThanOrEqual(5)
  })

  it('renders theme toggle button', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const toggle = wrapper.find('.theme-toggle')
    expect(toggle.exists()).toBe(true)
  })

  it('toggles theme on click', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const toggle = wrapper.find('.theme-toggle')
    const textBefore = toggle.text()
    await toggle.trigger('click')
    const textAfter = toggle.text()
    expect(textBefore).not.toBe(textAfter)
  })

  it('renders hamburger menu button', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const hamburger = wrapper.find('.hamburger')
    expect(hamburger.exists()).toBe(true)
    expect(hamburger.attributes('aria-label')).toBe('Menu')
  })

  it('toggles mobile drawer on hamburger click', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })

    expect(wrapper.find('.mobile-drawer').exists()).toBe(false)
    await wrapper.find('.hamburger').trigger('click')
    expect(wrapper.find('.mobile-drawer').exists()).toBe(true)
  })

  it('highlights the active nav link', async () => {
    const router = makeRouter()
    await router.push('/launches')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const activeLinks = wrapper.findAll('.nav-link.active')
    expect(activeLinks.length).toBeGreaterThanOrEqual(1)
    expect(activeLinks.some((l) => l.text().includes('Launches'))).toBe(true)
  })

  it('renders explore dropdown with more items', async () => {
    const router = makeRouter()
    await router.push('/')
    await router.isReady()

    const wrapper = mount(AppHeader, {
      global: { plugins: [router] },
    })
    const dropdown = wrapper.find('.nav-dropdown')
    expect(dropdown.exists()).toBe(true)
    expect(dropdown.text()).toContain('Explore')
  })
})
