import { describe, it, expect } from 'vitest'

const routeNames = [
  { path: '/', name: 'Overview' },
  { path: '/launches', name: 'Launches' },
  { path: '/fleet', name: 'Fleet' },
  { path: '/starlink', name: 'Starlink' },
  { path: '/economics', name: 'Economics' },
  { path: '/launches/:id', name: 'LaunchDetail' },
  { path: '/rockets/:id', name: 'RocketDetail' },
  { path: '/history', name: 'History' },
  { path: '/landing', name: 'Landing' },
  { path: '/starman', name: 'Starman' },
  { path: '/emissions', name: 'Emissions' },
]

describe('Router configuration', () => {
  it('exports a router instance with all 11 routes', async () => {
    const mod = await import('@/router/index')
    const router = mod.default
    expect(router).toBeDefined()

    const routes = router.getRoutes()
    expect(routes.length).toBe(routeNames.length)
  })

  it.each(routeNames)('has route "$name" at path "$path"', async ({ path, name }) => {
    const mod = await import('@/router/index')
    const router = mod.default
    const match = router.getRoutes().find((r) => r.name === name)
    expect(match).toBeDefined()
    expect(match!.path).toBe(path)
  })

  it('all routes use lazy-loaded components', async () => {
    const mod = await import('@/router/index')
    const router = mod.default
    for (const route of router.getRoutes()) {
      expect(route.components).toBeDefined()
    }
  })
})
