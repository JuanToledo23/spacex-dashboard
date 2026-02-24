import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
  }
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
    },
  }
})

const mockApi = axios.create() as any

describe('API functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetchDashboard calls GET /dashboard', async () => {
    mockApi.get.mockResolvedValue({ data: { total_launches: 200 } })
    const { fetchDashboard } = await import('@/api')
    const result = await fetchDashboard()
    expect(result).toEqual({ total_launches: 200 })
  })

  it('fetchRockets calls GET /rockets', async () => {
    mockApi.get.mockResolvedValue({ data: [{ id: 'r1' }] })
    const { fetchRockets } = await import('@/api')
    const result = await fetchRockets()
    expect(result).toEqual([{ id: 'r1' }])
  })

  it('fetchLaunches calls GET /launches with params', async () => {
    mockApi.get.mockResolvedValue({ data: { items: [], total: 0 } })
    const { fetchLaunches } = await import('@/api')
    const result = await fetchLaunches({ page: 2, limit: 10 })
    expect(result).toEqual({ items: [], total: 0 })
    expect(mockApi.get).toHaveBeenCalledWith('/launches', { params: { page: 2, limit: 10 } })
  })

  it('fetchStarlink calls GET /starlink', async () => {
    mockApi.get.mockResolvedValue({ data: { items: [] } })
    const { fetchStarlink } = await import('@/api')
    await fetchStarlink({ page: 1 })
    expect(mockApi.get).toHaveBeenCalledWith('/starlink', { params: { page: 1 } })
  })

  it('fetchStarlinkStats calls GET /starlink/stats', async () => {
    mockApi.get.mockResolvedValue({ data: { total: 5000 } })
    const { fetchStarlinkStats } = await import('@/api')
    const result = await fetchStarlinkStats()
    expect(result).toEqual({ total: 5000 })
  })

  it('fetchStarlinkPositions calls GET /starlink/positions', async () => {
    mockApi.get.mockResolvedValue({ data: [] })
    const { fetchStarlinkPositions } = await import('@/api')
    const result = await fetchStarlinkPositions()
    expect(result).toEqual([])
  })

  it('fetchFleetStats calls GET /cores/stats', async () => {
    mockApi.get.mockResolvedValue({ data: { total_cores: 10 } })
    const { fetchFleetStats } = await import('@/api')
    const result = await fetchFleetStats()
    expect(result).toEqual({ total_cores: 10 })
  })

  it('fetchLaunchDetail calls GET /launches/:id', async () => {
    mockApi.get.mockResolvedValue({ data: { id: 'l1' } })
    const { fetchLaunchDetail } = await import('@/api')
    const result = await fetchLaunchDetail('l1')
    expect(result).toEqual({ id: 'l1' })
    expect(mockApi.get).toHaveBeenCalledWith('/launches/l1')
  })

  it('fetchRocketDetail calls GET /rockets/:id', async () => {
    mockApi.get.mockResolvedValue({ data: { id: 'r1' } })
    const { fetchRocketDetail } = await import('@/api')
    const result = await fetchRocketDetail('r1')
    expect(result).toEqual({ id: 'r1' })
  })

  it('fetchEconomics calls GET /economics', async () => {
    mockApi.get.mockResolvedValue({ data: { total_estimated_spend: 1e9 } })
    const { fetchEconomics } = await import('@/api')
    const result = await fetchEconomics()
    expect(result.total_estimated_spend).toBe(1e9)
  })

  it('fetchHistory calls GET /history', async () => {
    mockApi.get.mockResolvedValue({ data: { events: [] } })
    const { fetchHistory } = await import('@/api')
    const result = await fetchHistory()
    expect(result).toEqual({ events: [] })
  })

  it('fetchLanding calls GET /landing', async () => {
    mockApi.get.mockResolvedValue({ data: { stats: {}, landpads: [] } })
    const { fetchLanding } = await import('@/api')
    const result = await fetchLanding()
    expect(result).toBeDefined()
  })

  it('fetchRoadster calls GET /roadster', async () => {
    mockApi.get.mockResolvedValue({ data: { name: 'Tesla' } })
    const { fetchRoadster } = await import('@/api')
    const result = await fetchRoadster()
    expect(result.name).toBe('Tesla')
  })

  it('fetchEmissions calls GET /emissions', async () => {
    mockApi.get.mockResolvedValue({ data: { total_co2_tonnes: 100 } })
    const { fetchEmissions } = await import('@/api')
    const result = await fetchEmissions()
    expect(result.total_co2_tonnes).toBe(100)
  })

  it('fetchAiStatus calls GET /ai/status', async () => {
    mockApi.get.mockResolvedValue({ data: { available: true } })
    const { fetchAiStatus } = await import('@/api')
    const result = await fetchAiStatus()
    expect(result.available).toBe(true)
  })

  it('sendChatMessage calls POST /ai/chat', async () => {
    mockApi.post.mockResolvedValue({ data: { response: 'Hello' } })
    const { sendChatMessage } = await import('@/api')
    const result = await sendChatMessage('hi', [])
    expect(result.response).toBe('Hello')
    expect(mockApi.post).toHaveBeenCalledWith('/ai/chat', { message: 'hi', history: [] })
  })

  it('fetchFunFact calls GET /ai/fun-fact', async () => {
    mockApi.get.mockResolvedValue({ data: { fact: 'Cool fact' } })
    const { fetchFunFact } = await import('@/api')
    const result = await fetchFunFact()
    expect(result.fact).toBe('Cool fact')
  })
})
