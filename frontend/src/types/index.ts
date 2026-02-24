// ─── Generic ────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

// ─── Dashboard ──────────────────────────────────────────────────────────────

export interface LaunchAggregate {
  year: number
  total: number
  successes: number
  failures: number
}

export interface RocketLaunchCount {
  rocket: string
  count: number
}

export interface SiteLaunchCount {
  site: string
  count: number
}

export interface Insight {
  id: string
  type: string
  text: string
  payload?: Record<string, unknown> | null
  action_type?: string | null
  priority?: string | null
  domains?: string[]
}

export interface LaunchHighlight {
  id: string
  name: string
  date_utc: string
  success?: boolean | null
  upcoming: boolean
  rocket_name?: string | null
  details?: string | null
  patch_small?: string | null
  webcast?: string | null
  flickr_images?: string[]
}

export interface LaunchpadSummary {
  id: string
  name: string
  full_name: string
  locality: string
  region: string
  latitude: number
  longitude: number
  launch_attempts: number
  launch_successes: number
  status: string
}

export interface DashboardResponse {
  total_rockets: number
  active_rockets: number
  total_launches: number
  successful_launches: number
  failed_launches: number
  upcoming_launches: number
  success_rate: number
  launches_by_year: LaunchAggregate[]
  launches_by_rocket: RocketLaunchCount[]
  launches_by_site: SiteLaunchCount[]
  total_starlink: number
  active_cores: number
  total_landings: number
  latest_launch: LaunchHighlight | null
  next_launch: LaunchHighlight | null
  recent_launches: LaunchHighlight[]
  insights: Insight[]
  launchpads: LaunchpadSummary[]
}

// ─── Launches ───────────────────────────────────────────────────────────────

export interface LaunchSummary {
  id: string
  name: string
  date_utc: string
  success: boolean | null
  upcoming: boolean
  rocket_id: string
  rocket_name: string | null
  details: string | null
  patch_small: string | null
}

export interface PayloadSummary {
  id: string
  name: string
  type?: string | null
  customers: string[]
  mass_kg?: number | null
  orbit?: string | null
  regime?: string | null
}

export interface CoreDetail {
  serial?: string | null
  flight?: number | null
  reused?: boolean | null
  landing_attempt?: boolean | null
  landing_success?: boolean | null
  landing_type?: string | null
}

export interface CrewMember {
  id: string
  name: string
  agency?: string | null
  image?: string | null
  role?: string | null
}

export interface LaunchLinks {
  webcast?: string | null
  article?: string | null
  wikipedia?: string | null
  presskit?: string | null
  reddit_campaign?: string | null
  flickr_original?: string[]
  patch_small?: string | null
  patch_large?: string | null
}

export interface LaunchFailure {
  time?: number | null
  altitude?: number | null
  reason?: string | null
}

export interface LaunchDetail {
  id: string
  flight_number: number
  name: string
  date_utc: string
  success: boolean | null
  upcoming: boolean
  details: string | null
  rocket_id: string
  rocket_name: string | null
  launchpad_name: string | null
  cores: CoreDetail[]
  payloads: PayloadSummary[]
  crew: CrewMember[]
  links: LaunchLinks | null
  failures: LaunchFailure[]
  fairings_recovered: boolean | null
  fairings_reused: boolean | null
  static_fire_date_utc: string | null
}

// ─── Rockets ────────────────────────────────────────────────────────────────

export interface RocketSummary {
  id: string
  name: string
  type: string
  active: boolean
  success_rate_pct: number
  launch_count: number
  cost_per_launch?: number | null
  first_flight?: string | null
  description?: string | null
  flickr_images: string[]
  height_meters?: number | null
  diameter_meters?: number | null
  mass_kg?: number | null
}

export interface EngineSpec {
  number?: number | null
  type?: string | null
  version?: string | null
  propellant_1?: string | null
  propellant_2?: string | null
  thrust_sea_level_kn?: number | null
  thrust_vacuum_kn?: number | null
  isp_sea_level?: number | null
  isp_vacuum?: number | null
  thrust_to_weight?: number | null
}

export interface PayloadWeight {
  id: string
  name: string
  kg: number
  lb: number
}

export interface StageSpec {
  reusable?: boolean | null
  engines?: number | null
  fuel_amount_tons?: number | null
  burn_time_sec?: number | null
  thrust_sea_level_kn?: number | null
  thrust_vacuum_kn?: number | null
}

export interface RocketDetail {
  id: string
  name: string
  type: string
  active: boolean
  stages: number
  boosters: number
  cost_per_launch?: number | null
  success_rate_pct: number
  first_flight?: string | null
  country?: string | null
  description?: string | null
  wikipedia?: string | null
  flickr_images: string[]
  height_meters?: number | null
  diameter_meters?: number | null
  mass_kg?: number | null
  engines?: EngineSpec | null
  payload_weights: PayloadWeight[]
  first_stage?: StageSpec | null
  second_stage?: StageSpec | null
  landing_legs_number?: number | null
  landing_legs_material?: string | null
  launch_count: number
}

// ─── Starlink ───────────────────────────────────────────────────────────────

export interface StarlinkSatellite {
  id: string
  object_name?: string | null
  version?: string | null
  height_km?: number | null
  latitude?: number | null
  longitude?: number | null
  velocity_kms?: number | null
  launch_id?: string | null
}

export interface StarlinkPosition {
  id: string
  object_name?: string | null
  latitude: number
  longitude: number
  height_km?: number | null
  velocity_kms?: number | null
  version?: string | null
}

export interface StarlinkVersionCount {
  version: string | null
  count: number
}

export interface StarlinkStats {
  total: number
  by_version: StarlinkVersionCount[]
  avg_height_km: number
}

// ─── Fleet / Cores ──────────────────────────────────────────────────────────

export interface CoreSummary {
  id: string
  serial: string
  status: string
  reuse_count: number
  rtls_landings: number
  asds_landings: number
  total_landings: number
  total_attempts: number
  launches: number
}

export interface FleetStats {
  total_cores: number
  active_cores: number
  retired_cores: number
  lost_cores: number
  total_landings: number
  total_landing_attempts: number
  landing_success_rate: number
  rtls_landings: number
  rtls_attempts: number
  asds_landings: number
  asds_attempts: number
  most_reused: CoreSummary[]
}

// ─── Economics ──────────────────────────────────────────────────────────────

export interface CostByVehicle {
  rocket_id: string
  rocket_name: string
  cost_per_launch: number
  launches: number
  total_spend: number
  payload_kg_leo?: number | null
  cost_per_kg_leo?: number | null
}

export interface AnnualSpend {
  year: number
  launches: number
  total_spend: number
  avg_cost: number
}

export interface CustomerVolume {
  customer: string
  payloads: number
  total_mass_kg: number
}

export interface OrbitMass {
  orbit: string
  total_mass_kg: number
  payloads: number
}

export interface EconomicsResponse {
  total_estimated_spend: number
  total_launches: number
  total_payloads: number
  total_mass_launched_kg: number
  avg_cost_per_launch: number
  lowest_cost_per_kg: number
  lowest_cost_vehicle: string
  cost_by_vehicle: CostByVehicle[]
  annual_spend: AnnualSpend[]
  top_customers: CustomerVolume[]
  mass_by_orbit: OrbitMass[]
}

// ─── Emissions ──────────────────────────────────────────────────────────────

export interface EmissionsByVehicle {
  rocket_id: string
  rocket_name: string
  fuel_type: string
  fuel_per_launch_tonnes: number
  co2_per_launch_tonnes: number
  launches: number
  total_co2_tonnes: number
  payload_kg_leo?: number | null
  co2_per_kg_leo?: number | null
}

export interface AnnualEmissions {
  year: number
  launches: number
  co2_tonnes: number
  fuel_burned_tonnes: number
  reuse_savings_tonnes: number
}

export interface FuelBreakdown {
  fuel_type: string
  fuel_tonnes: number
  co2_tonnes: number
  percentage: number
}

export interface EmissionsResponse {
  total_co2_tonnes: number
  total_fuel_tonnes: number
  co2_per_launch: number
  reuse_co2_saved_tonnes: number
  total_reuses: number
  total_launches: number
  emissions_by_vehicle: EmissionsByVehicle[]
  annual_emissions: AnnualEmissions[]
  fuel_breakdown: FuelBreakdown[]
}

// ─── Landing ────────────────────────────────────────────────────────────────

export interface LandpadSummary {
  id: string
  name: string
  full_name: string
  type: string
  status: string
  locality?: string | null
  region?: string | null
  latitude: number
  longitude: number
  landing_attempts: number
  landing_successes: number
  success_rate: number
}

export interface LandingStats {
  total_attempts: number
  total_successes: number
  overall_success_rate: number
  rtls_attempts: number
  rtls_successes: number
  asds_attempts: number
  asds_successes: number
}

export interface LandingResponse {
  stats: LandingStats
  landpads: LandpadSummary[]
}

// ─── History ────────────────────────────────────────────────────────────────

export interface HistoryEvent {
  id: string
  title: string
  event_date_utc: string
  details?: string | null
  article?: string | null
  wikipedia?: string | null
}

export interface HistoryResponse {
  events: HistoryEvent[]
  total: number
}

// ─── Roadster ───────────────────────────────────────────────────────────────

export interface RoadsterData {
  name: string
  launch_date_utc: string
  speed_kph: number
  earth_distance_km: number
  earth_distance_mi: number
  mars_distance_km: number
  mars_distance_mi: number
  orbit_type: string
  period_days: number
  apoapsis_au: number
  periapsis_au: number
  semi_major_axis_au?: number | null
  eccentricity?: number | null
  inclination?: number | null
  details?: string | null
  wikipedia?: string | null
  video?: string | null
  flickr_images: string[]
}

// ─── Query Params ───────────────────────────────────────────────────────────

export interface LaunchQueryParams {
  page?: number
  limit?: number
  success?: boolean | null
  upcoming?: boolean | null
  rocket_id?: string | null
}

export interface StarlinkQueryParams {
  page?: number
  limit?: number
  version?: string | null
}

// ─── Component Helpers ──────────────────────────────────────────────────────

export interface TableColumn {
  key: string
  label: string
}

export interface NavItem {
  to: string
  label: string
  icon: string
}

// ─── AI ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatResponse {
  response: string
}

export interface AiStatusResponse {
  available: boolean
}

export interface FunFactResponse {
  fact: string
}

export interface AppNotification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info' | 'launch'
  title: string
  message: string
  timestamp: string
}
