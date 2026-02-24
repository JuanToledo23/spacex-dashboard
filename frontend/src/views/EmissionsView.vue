<template>
  <section class="emissions-page">
    <div
      v-if="loading"
      class="loading-state"
    >
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <SkeletonLoader
        variant="chart"
        height="320px"
      />
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px">
        <SkeletonLoader
          variant="stat"
          :count="3"
        />
        <SkeletonLoader
          variant="chart"
          height="260px"
        />
      </div>
    </div>

    <template v-else-if="data">
      <!-- Header -->
      <div class="emissions-header">
        <div class="header-tag">
          <span class="tag-dot" />
          <span class="tag-text">ESTIMATED DATA</span>
        </div>
        <h1 class="header-title">
          Environmental Impact
        </h1>
        <p class="header-sub">
          Estimated CO&#x2082; emissions from SpaceX launch operations, based on rocket fuel data and documented emission factors.
        </p>
      </div>

      <SectionNav :sections="emissionsSections" />

      <!-- Hero Stats -->
      <div
        id="emit-stats"
        data-section-nav
        class="stats-grid"
      >
        <div class="stat-card surface">
          <span class="stat-label">Total CO&#x2082; (all-time)</span>
          <span class="stat-value">{{ formatNum(data.total_co2_tonnes) }}</span>
          <span class="stat-unit">tonnes</span>
        </div>
        <div class="stat-card surface">
          <span class="stat-label">Per Launch</span>
          <span class="stat-value">{{ formatNum(data.co2_per_launch) }}</span>
          <span class="stat-unit">tonnes CO&#x2082;</span>
        </div>
        <div class="stat-card surface accent-green">
          <span class="stat-label">Reuse Saved</span>
          <span class="stat-value">{{ formatNum(data.reuse_co2_saved_tonnes) }}</span>
          <span class="stat-unit">tonnes CO&#x2082;</span>
        </div>
        <div class="stat-card surface">
          <span class="stat-label">Total Fuel</span>
          <span class="stat-value">{{ formatNum(data.total_fuel_tonnes) }}</span>
          <span class="stat-unit">tonnes burned</span>
        </div>
      </div>

      <!-- Annual Emissions Trend -->
      <div
        id="emit-trend"
        data-section-nav
        class="section-block surface section-gap"
      >
        <div class="section-head">
          <h2 class="section-title">
            Annual Emissions Trend
          </h2>
          <span class="section-note">{{ data.total_launches }} launches analyzed</span>
        </div>
        <EmissionsTimelineChart
          :data="data.annual_emissions"
          :height="340"
        />
      </div>

      <!-- Two-column: Emissions by Vehicle + CO2 Intensity -->
      <div
        id="emit-vehicles"
        data-section-nav
        class="two-col section-gap"
      >
        <div class="section-block surface">
          <h2 class="section-title">
            Emissions by Vehicle
          </h2>
          <div class="vehicle-list">
            <div
              v-for="v in data.emissions_by_vehicle"
              :key="v.rocket_id"
              class="vehicle-row"
            >
              <div class="vr-header">
                <span class="vr-name">{{ v.rocket_name }}</span>
                <span class="vr-total">{{ formatNum(v.total_co2_tonnes) }} tonnes</span>
              </div>
              <div class="vr-bar-track">
                <div
                  class="vr-bar-fill"
                  :style="{ width: vehicleBarWidth(v.total_co2_tonnes) }"
                />
              </div>
              <div class="vr-meta">
                <span class="vr-tag">{{ v.fuel_type }}</span>
                <span class="vr-detail">{{ v.launches }} launches &middot; {{ formatNum(v.co2_per_launch_tonnes) }} tonnes each</span>
              </div>
            </div>
          </div>
        </div>

        <div class="section-block surface">
          <h2 class="section-title">
            CO&#x2082; Intensity
            <InfoTip>How much CO2 is emitted for each kilogram of cargo delivered to orbit — lower means more environmentally efficient.</InfoTip>
          </h2>
          <p class="intensity-sub">
            kg CO&#x2082; per kg payload to LEO
            <InfoTip>LEO = Low Earth Orbit (200–2,000 km). The standard reference orbit for comparing launch efficiency.</InfoTip>
          </p>
          <div class="intensity-list">
            <div
              v-for="v in vehiclesWithIntensity"
              :key="v.rocket_id"
              class="intensity-row"
            >
              <div class="ir-header">
                <span class="ir-name">{{ v.rocket_name }}</span>
                <span class="ir-val">{{ v.co2_per_kg_leo }} kg</span>
              </div>
              <div class="ir-bar-track">
                <div
                  class="ir-bar-fill"
                  :style="{ width: intensityBarWidth(v.co2_per_kg_leo) }"
                />
              </div>
            </div>
          </div>
          <p class="intensity-note">
            Lower is better. Based on LEO capacity.
          </p>
        </div>
      </div>

      <!-- Propellant Mix -->
      <div
        id="emit-fuel"
        data-section-nav
        class="section-block surface fuel-section section-gap"
      >
        <div class="fuel-content">
          <div class="fuel-chart-wrap">
            <h2 class="section-title">
              Propellant Mix
              <InfoTip>The combination of fuel and oxidizer used by each rocket type. Different propellants produce different amounts of CO2.</InfoTip>
            </h2>
            <FuelBreakdownChart
              :data="data.fuel_breakdown"
              :height="280"
            />
          </div>
          <div class="fuel-details">
            <div
              v-for="(fb, i) in data.fuel_breakdown"
              :key="fb.fuel_type"
              class="fuel-item"
            >
              <div
                class="fuel-item-accent"
                :style="{ background: fuelColors[i] }"
              />
              <div class="fuel-item-body">
                <div class="fuel-row-top">
                  <span class="fuel-name">{{ fb.fuel_type }}</span>
                  <span
                    class="fuel-pct"
                    :style="{ color: fuelColors[i] }"
                  >{{ fb.percentage }}%</span>
                </div>
                <div class="fuel-row-stats">
                  <div class="fuel-stat-pair">
                    <span class="fuel-stat-label">Fuel</span>
                    <span class="fuel-stat-val">{{ formatNum(fb.fuel_tonnes) }} tonnes</span>
                  </div>
                  <div class="fuel-stat-pair">
                    <span class="fuel-stat-label">CO&#x2082;</span>
                    <span class="fuel-stat-val">{{ formatNum(fb.co2_tonnes) }} tonnes</span>
                  </div>
                  <div class="fuel-stat-pair">
                    <span class="fuel-stat-label">Ratio</span>
                    <span class="fuel-stat-val">{{ fuelRatio(fb) }} kg/kg</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Contextual equivalence -->
            <div class="fuel-equivalence">
              <div
                class="equiv-icon"
                aria-hidden="true"
              >
                &#127758;
              </div>
              <div class="equiv-content">
                <span class="equiv-title">In Context</span>
                <span class="equiv-val">Equivalent to {{ formatNum(carYearsEquiv) }} cars driving for one year</span>
                <span class="equiv-note">Based on 4.6 tonnes CO&#x2082; per car per year</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reuse Impact -->
      <div
        id="emit-reuse"
        data-section-nav
        class="section-block surface reuse-section section-gap"
      >
        <h2 class="section-title">
          Reuse Savings
        </h2>
        <div class="reuse-grid">
          <div class="reuse-item">
            <span class="reuse-val green">{{ data.total_reuses }}</span>
            <span class="reuse-lbl">Core reuses</span>
          </div>
          <div class="reuse-item">
            <span class="reuse-val green">{{ formatNum(data.reuse_co2_saved_tonnes) }} tonnes</span>
            <span class="reuse-lbl">Manufacturing CO&#x2082; avoided</span>
          </div>
          <div class="reuse-item">
            <span class="reuse-val">60 tonnes</span>
            <span class="reuse-lbl">CO&#x2082; per new booster</span>
          </div>
        </div>
        <p class="reuse-note">
          Each time a Falcon 9 booster is reused instead of building a new one, an estimated 60 tonnes of manufacturing CO&#x2082; is avoided.
        </p>
      </div>

      <!-- Methodology -->
      <div
        id="emit-method"
        data-section-nav
        class="section-block surface methodology section-gap"
      >
        <h2 class="section-title">
          Methodology &amp; Sources
        </h2>
        <div class="method-content">
          <p>These are <strong>estimates</strong>, not official SpaceX data. Emissions are calculated from publicly available rocket specifications and documented emission factors:</p>
          <ul class="method-list">
            <li><strong>RP-1/LOX</strong> (Falcon 9, Falcon Heavy): O/F ratio ~2.27:1. RP-1 fraction ~30.6% of propellant mass. CO&#x2082; emission: 3.15 kg per kg RP-1 burned.</li>
            <li><strong>Liquid Methane/LOX</strong> (Starship): O/F ratio ~3.6:1. CH&#x2084; fraction ~21.7%. CO&#x2082; emission: 2.75 kg per kg methane.</li>
            <li><strong>Fuel amounts</strong> sourced from SpaceX API rocket data (<code>first_stage.fuel_amount_tons</code>, <code>second_stage.fuel_amount_tons</code>).</li>
            <li><strong>Reuse savings</strong>: Conservative estimate of 60 tonnes CO&#x2082; per booster manufacturing cycle avoided (industry lifecycle analyses).</li>
            <li>Does not include: ground operations, transportation logistics, upper atmosphere effects (black carbon, water vapor at altitude), or Scope 3 supply chain emissions.</li>
          </ul>
          <p class="method-disclaimer">
            Sources: NASA Technical Reports, ESA Space Debris Environment Report, Rocket Propulsion Elements (Sutton &amp; Biblarz), peer-reviewed lifecycle analyses of launch vehicles.
          </p>
        </div>
      </div>
    </template>

    <ErrorState
      v-else
      message="Unable to load emissions data."
      @retry="loadData"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fetchEmissions } from '@/api'
import EmissionsTimelineChart from '@/components/charts/EmissionsTimelineChart.vue'
import FuelBreakdownChart from '@/components/charts/FuelBreakdownChart.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import SectionNav from '@/components/common/SectionNav.vue'
import type { EmissionsResponse, FuelBreakdown as FuelBreakdownType } from '@/types'

const emissionsSections = [
  { id: 'emit-stats', label: 'Overview' },
  { id: 'emit-trend', label: 'Annual Trend' },
  { id: 'emit-vehicles', label: 'By Vehicle' },
  { id: 'emit-fuel', label: 'Propellant' },
  { id: 'emit-reuse', label: 'Reuse Impact' },
  { id: 'emit-method', label: 'Methodology' },
]

const data = ref<EmissionsResponse | null>(null)
const loading = ref(true)

const fuelColors: string[] = ['#d4915c', '#5b8def', '#22c55e', '#ef4444']

async function loadData(): Promise<void> {
  loading.value = true
  data.value = null
  try {
    data.value = await fetchEmissions()
  } catch (e) {
    console.error('Failed to fetch emissions:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function formatNum(n: number | null | undefined): string {
  if (!n && n !== 0) return '0'
  return Math.round(n).toLocaleString()
}

function fuelRatio(fb: FuelBreakdownType): string {
  if (!fb.fuel_tonnes || fb.fuel_tonnes === 0) return '0'
  return (fb.co2_tonnes / fb.fuel_tonnes).toFixed(2)
}

const carYearsEquiv = computed(() => {
  if (!data.value) return 0
  return Math.round(data.value.total_co2_tonnes / 4.6)
})

const vehiclesWithIntensity = computed(() => {
  if (!data.value) return []
  return data.value.emissions_by_vehicle
    .filter(v => v.co2_per_kg_leo)
    .sort((a, b) => (a.co2_per_kg_leo ?? 0) - (b.co2_per_kg_leo ?? 0))
})

function vehicleBarWidth(total: number): string {
  if (!data.value) return '0%'
  const max = Math.max(...data.value.emissions_by_vehicle.map(v => v.total_co2_tonnes))
  return Math.round((total / max) * 100) + '%'
}

function intensityBarWidth(val: number | null | undefined): string {
  if (!val) return '0%'
  const max = Math.max(...vehiclesWithIntensity.value.map(v => v.co2_per_kg_leo ?? 0))
  return Math.round((val / max) * 100) + '%'
}
</script>

<style scoped>
.emissions-page {
  max-width: 1080px;
  margin: 0 auto;
}

/* Header */
.emissions-header {
  margin-bottom: 32px;
  padding: 0 4px;
}

.header-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--warning, #f59e0b);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.tag-text {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  color: var(--warning, #f59e0b);
}

.header-title {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 8px;
}

.header-sub {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 640px;
  margin: 0;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  margin-bottom: 2px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 12px;
  gap: 2px;
}

.stat-card.accent-green .stat-value {
  color: var(--success);
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.stat-unit {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Sections */
.section-block {
  margin-top: 2px;
  border-radius: var(--radius);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 16px;
}

.section-note {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Two column */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  margin-top: 2px;
}

/* Vehicle bars */
.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.vehicle-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vr-name {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.vr-total {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--accent);
}

.vr-bar-track {
  height: 8px;
  background: var(--chart-track, rgba(255,255,255,0.06));
  border-radius: 4px;
  overflow: hidden;
}

.vr-bar-fill {
  height: 100%;
  background: var(--accent);
  opacity: 0.7;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.vr-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vr-tag {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--accent);
  letter-spacing: 0.04em;
  padding: 1px 6px;
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
  border-radius: 3px;
}

.vr-detail {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Intensity */
.intensity-sub {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin: -10px 0 16px;
}

.intensity-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.intensity-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ir-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ir-name {
  font-family: var(--font-display);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
}

.ir-val {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text);
}

.ir-bar-track {
  height: 8px;
  background: var(--chart-track, rgba(255,255,255,0.06));
  border-radius: 4px;
  overflow: hidden;
}

.ir-bar-fill {
  height: 100%;
  background: var(--accent-blue, #5b8def);
  opacity: 0.65;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.intensity-note {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  margin-top: 12px;
}

/* Propellant Mix */
.fuel-section .section-title {
  margin-bottom: 8px;
}

.fuel-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: start;
}

.fuel-chart-wrap {
  display: flex;
  flex-direction: column;
}

.fuel-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fuel-item {
  display: flex;
  align-items: stretch;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color 0.2s;
}

.fuel-item:hover {
  border-color: var(--border-strong);
}

.fuel-item-accent {
  width: 4px;
  flex-shrink: 0;
}

.fuel-item-body {
  flex: 1;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fuel-row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fuel-name {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.fuel-pct {
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 700;
}

.fuel-row-stats {
  display: flex;
  gap: 16px;
}

.fuel-stat-pair {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.fuel-stat-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.fuel-stat-val {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text);
}

.fuel-equivalence {
  display: flex;
  align-items: center;
  gap: 14px;
  background: color-mix(in srgb, var(--accent) 8%, var(--bg-elevated));
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-top: 4px;
}

.equiv-icon {
  font-size: 1.6rem;
  line-height: 1;
}

.equiv-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.equiv-title {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.equiv-val {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--accent);
}

.equiv-note {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--text-muted);
}

/* Reuse */
.reuse-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 16px;
}

.reuse-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 4px;
}

.reuse-val {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text);
}

.reuse-val.green {
  color: var(--success);
}

.reuse-lbl {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  letter-spacing: 0.03em;
}

.reuse-note {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  text-align: center;
  margin: 0;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

/* Methodology */
.methodology .section-title {
  margin-bottom: 12px;
}

.method-content {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.method-content p {
  margin: 0 0 12px;
}

.method-content strong {
  color: var(--text);
  font-weight: 600;
}

.method-list {
  margin: 0 0 16px;
  padding-left: 20px;
}

.method-list li {
  margin-bottom: 8px;
}

.method-list code {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  padding: 1px 5px;
  background: var(--bg-elevated);
  border-radius: 3px;
  color: var(--accent);
}

.method-disclaimer {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  padding-top: 12px;
  border-top: 1px solid var(--border);
  margin-bottom: 0;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120px 24px 48px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .two-col { grid-template-columns: 1fr; }
  .fuel-content { grid-template-columns: 1fr; }
  .reuse-grid { grid-template-columns: 1fr; }
  .header-title { font-size: 1.8rem; }
  .fuel-row-stats { gap: 10px; }
}

@media (max-width: 640px) {
  .header-title { font-size: 1.4rem; }
  .stat-value { font-size: 1.4rem; }
  .fuel-row-stats { flex-wrap: wrap; gap: 8px; }
  .reuse-val { font-size: 1.3rem; }
}
</style>
