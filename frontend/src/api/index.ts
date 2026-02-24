import axios from 'axios'
import type {
  DashboardResponse,
  RocketSummary,
  LaunchSummary,
  LaunchDetail,
  RocketDetail,
  StarlinkSatellite,
  StarlinkPosition,
  StarlinkStats,
  FleetStats,
  EconomicsResponse,
  HistoryResponse,
  LandingResponse,
  RoadsterData,
  EmissionsResponse,
  PaginatedResponse,
  LaunchQueryParams,
  StarlinkQueryParams,
  ChatMessage,
  ChatResponse,
  AiStatusResponse,
  FunFactResponse,
} from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
})

export const fetchDashboard = (): Promise<DashboardResponse> =>
  api.get('/dashboard').then((r) => r.data)

export const fetchRockets = (): Promise<RocketSummary[]> =>
  api.get('/rockets').then((r) => r.data)

export const fetchLaunches = (params: LaunchQueryParams = {}): Promise<PaginatedResponse<LaunchSummary>> =>
  api.get('/launches', { params }).then((r) => r.data)

export const fetchStarlink = (params: StarlinkQueryParams = {}): Promise<PaginatedResponse<StarlinkSatellite>> =>
  api.get('/starlink', { params }).then((r) => r.data)

export const fetchStarlinkStats = (): Promise<StarlinkStats> =>
  api.get('/starlink/stats').then((r) => r.data)

export const fetchStarlinkPositions = (): Promise<StarlinkPosition[]> =>
  api.get('/starlink/positions').then((r) => r.data)

export const fetchFleetStats = (): Promise<FleetStats> =>
  api.get('/cores/stats').then((r) => r.data)

export const fetchLaunchDetail = (id: string): Promise<LaunchDetail> =>
  api.get(`/launches/${id}`).then((r) => r.data)

export const fetchRocketDetail = (id: string): Promise<RocketDetail> =>
  api.get(`/rockets/${id}`).then((r) => r.data)

export const fetchEconomics = (): Promise<EconomicsResponse> =>
  api.get('/economics').then((r) => r.data)

export const fetchHistory = (): Promise<HistoryResponse> =>
  api.get('/history').then((r) => r.data)

export const fetchLanding = (): Promise<LandingResponse> =>
  api.get('/landing').then((r) => r.data)

export const fetchRoadster = (): Promise<RoadsterData> =>
  api.get('/roadster').then((r) => r.data)

export const fetchEmissions = (): Promise<EmissionsResponse> =>
  api.get('/emissions').then((r) => r.data)

export const fetchAiStatus = (): Promise<AiStatusResponse> =>
  api.get('/ai/status').then((r) => r.data)

export const sendChatMessage = (message: string, history: ChatMessage[]): Promise<ChatResponse> =>
  api.post('/ai/chat', { message, history }).then((r) => r.data)

export const fetchFunFact = (): Promise<FunFactResponse> =>
  api.get('/ai/fun-fact').then((r) => r.data)

export default api
