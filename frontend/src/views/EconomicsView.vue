<template>
  <div>
    <ErrorState
      v-if="error"
      :message="error"
      @retry="load"
    />

    <template v-else-if="loading">
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px">
        <SkeletonLoader
          variant="chart"
          height="280px"
        />
        <SkeletonLoader
          variant="chart"
          height="280px"
        />
      </div>
      <SkeletonLoader
        variant="table"
        :count="5"
      />
    </template>

    <template v-else-if="data">
      <!-- HEADER -->
      <div class="econ-header">
        <h1 class="econ-title">
          Launch Economics
        </h1>
        <p class="econ-sub">
          Estimated cost analysis (USD) based on published vehicle pricing and mission data.
        </p>
      </div>

      <SectionNav :sections="econSections" />

      <!-- HERO STAT CARDS -->
      <div
        id="econ-metrics"
        data-section-nav
        class="econ-stats-hero"
      >
        <div class="stat-card surface-dense">
          <span class="stat-val-hero mono">${{ formatBillions(data.total_estimated_spend) }}</span>
          <span class="stat-lbl">Total Spend (USD)</span>
          <span class="human-context">Similar to building {{ Math.round(data.total_estimated_spend / 1.5e9) }} football stadiums</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val-hero mono accent">${{ data.lowest_cost_per_kg.toLocaleString() }}/kg</span>
          <span class="stat-lbl">
            Lowest $/kg ({{ data.lowest_cost_vehicle }})
            <InfoTip>Cost to send one kilogram of cargo to space — like paying ${{ data.lowest_cost_per_kg.toLocaleString() }} to launch a bag of sugar.</InfoTip>
          </span>
        </div>
      </div>

      <!-- SECONDARY STAT CARDS -->
      <div class="econ-stats">
        <div class="stat-card surface-dense">
          <span class="stat-val mono">${{ formatMillions(data.avg_cost_per_launch) }}</span>
          <span class="stat-lbl">Avg Cost / Launch</span>
          <span class="human-context">Less than a single Boeing 737 aircraft</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val mono">{{ formatTons(data.total_mass_launched_kg) }}</span>
          <span class="stat-lbl">Total Mass Launched</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val mono">{{ data.total_payloads }}</span>
          <span class="stat-lbl">Total Payloads</span>
        </div>
      </div>

      <!-- COST PER KG -->
      <div
        id="econ-costkg"
        data-section-nav
        class="surface econ-section section-gap"
      >
        <span class="section-label">
          Cost per Kilogram to LEO
          <InfoTip>LEO = Low Earth Orbit (200–2,000 km altitude). Where the ISS and Starlink satellites orbit.</InfoTip>
        </span>
        <p class="section-hint">
          Logarithmic scale — lower is more efficient
        </p>
        <CostPerKgChart :data="data.cost_by_vehicle" />
      </div>

      <!-- ANNUAL SPEND + SPEND BY VEHICLE (side by side) -->
      <div
        id="econ-annual"
        data-section-nav
        class="econ-grid-2 section-gap"
      >
        <div class="surface econ-section">
          <span class="section-label">Annual Estimated Spend</span>
          <AnnualSpendChart
            :data="data.annual_spend"
            :height="260"
          />
        </div>
        <div class="surface econ-section">
          <span class="section-label">Spend by Vehicle</span>
          <SpendByVehicleChart :data="data.cost_by_vehicle" />
        </div>
      </div>

      <!-- MASS BY ORBIT -->
      <div
        id="econ-orbits"
        data-section-nav
        class="surface econ-section section-gap"
      >
        <span class="section-label">Mass Launched by Orbit</span>
        <MassByOrbitChart :data="data.mass_by_orbit" />
      </div>

      <!-- TOP CUSTOMERS TABLE -->
      <div
        id="econ-customers"
        data-section-nav
        class="surface econ-section section-gap"
      >
        <span class="section-label">Top Customers</span>
        <div class="customer-table-wrap">
          <table class="customer-table">
            <thead>
              <tr>
                <th class="col-rank">
                  #
                </th>
                <th class="col-name">
                  Customer
                </th>
                <th class="col-num">
                  Payloads
                </th>
                <th class="col-num">
                  Mass (kg)
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(c, i) in data.top_customers"
                :key="c.customer"
              >
                <td class="col-rank mono">
                  {{ i + 1 }}
                </td>
                <td class="col-name">
                  {{ c.customer }}
                </td>
                <td class="col-num mono">
                  {{ c.payloads }}
                </td>
                <td class="col-num mono">
                  {{ c.total_mass_kg.toLocaleString() }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- VEHICLE BREAKDOWN TABLE -->
      <div
        id="econ-vehicles"
        data-section-nav
        class="surface econ-section section-gap"
      >
        <span class="section-label">Cost per Vehicle</span>
        <div class="customer-table-wrap">
          <table class="customer-table">
            <thead>
              <tr>
                <th class="col-name">
                  Vehicle
                </th>
                <th class="col-num">
                  Launches
                </th>
                <th class="col-num">
                  Cost / Launch
                </th>
                <th class="col-num">
                  LEO Capacity <InfoTip>Maximum payload the vehicle can deliver to Low Earth Orbit.</InfoTip>
                </th>
                <th class="col-num">
                  $/kg to LEO <InfoTip>Cost per kilogram to Low Earth Orbit — the standard measure of launch affordability.</InfoTip>
                </th>
                <th class="col-num">
                  Total Spend
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="v in data.cost_by_vehicle"
                :key="v.rocket_id"
              >
                <td class="col-name vehicle-name">
                  {{ v.rocket_name }}
                </td>
                <td class="col-num mono">
                  {{ v.launches }}
                </td>
                <td class="col-num mono">
                  ${{ formatMillions(v.cost_per_launch) }}
                </td>
                <td class="col-num mono">
                  {{ v.payload_kg_leo ? v.payload_kg_leo.toLocaleString() + ' kg' : '—' }}
                </td>
                <td
                  class="col-num mono"
                  :class="{ accent: isLowest(v) }"
                >
                  ${{ v.cost_per_kg_leo ? v.cost_per_kg_leo.toLocaleString() : '—' }}
                </td>
                <td class="col-num mono">
                  ${{ formatMillions(v.total_spend) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchEconomics } from '@/api'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import CostPerKgChart from '@/components/charts/CostPerKgChart.vue'
import AnnualSpendChart from '@/components/charts/AnnualSpendChart.vue'
import SpendByVehicleChart from '@/components/charts/SpendByVehicleChart.vue'
import MassByOrbitChart from '@/components/charts/MassByOrbitChart.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import SectionNav from '@/components/common/SectionNav.vue'
import type { EconomicsResponse, CostByVehicle } from '@/types'

const econSections = [
  { id: 'econ-metrics', label: 'Key Metrics' },
  { id: 'econ-costkg', label: 'Cost per Kg' },
  { id: 'econ-annual', label: 'Annual Spend' },
  { id: 'econ-orbits', label: 'Mass by Orbit' },
  { id: 'econ-customers', label: 'Customers' },
  { id: 'econ-vehicles', label: 'Vehicles' },
]

const data = ref<EconomicsResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

function formatBillions(val: number): string {
  if (val >= 1e9) return (val / 1e9).toFixed(2) + 'B'
  return (val / 1e6).toFixed(0) + 'M'
}

function formatMillions(val: number): string {
  if (val >= 1e9) return (val / 1e9).toFixed(1) + 'B'
  if (val >= 1e6) return (val / 1e6).toFixed(0) + 'M'
  return val.toLocaleString()
}

function formatTons(kg: number): string {
  if (kg >= 1e6) return (kg / 1e6).toFixed(1) + 'M kg'
  return (kg / 1000).toFixed(0) + ' tonnes'
}

function isLowest(v: CostByVehicle): boolean {
  return !!v.cost_per_kg_leo && v.cost_per_kg_leo === data.value?.lowest_cost_per_kg
}

async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchEconomics()
  } catch {
    error.value = 'Failed to load economics data.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
/* HEADER */
.econ-header {
  margin-bottom: 16px;
}

.econ-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.econ-sub {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 6px;
  letter-spacing: 0.01em;
}

/* STAT CARDS */
.econ-stats-hero {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2px;
  margin-bottom: 2px;
}

.stat-val-hero {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}

.stat-val-hero.accent {
  color: var(--accent);
}

.econ-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  margin-bottom: 2px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 18px 10px;
  gap: 4px;
}

.stat-val {
  font-family: var(--font-mono);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}

.stat-val.accent {
  color: var(--accent);
}

.stat-lbl {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* SECTIONS */
.econ-section {
  margin-bottom: 2px;
}

.section-hint {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  opacity: 0.6;
  margin-top: -6px;
  margin-bottom: 10px;
}

/* TWO-COL GRID */
.econ-grid-2 {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 2px;
}

/* CUSTOMER TABLE */
.customer-table-wrap {
  overflow-x: auto;
}

.customer-table {
  width: 100%;
  border-collapse: collapse;
}

.customer-table th {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid var(--border-strong);
}

.customer-table td {
  font-family: var(--font-body);
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
}

.customer-table tbody tr:last-child td {
  border-bottom: none;
}

.col-rank {
  width: 36px;
  text-align: center !important;
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
}

.col-name {
  min-width: 120px;
}

.col-num {
  text-align: right !important;
  white-space: nowrap;
}

.vehicle-name {
  font-family: var(--font-display) !important;
  font-weight: 600;
  color: var(--text) !important;
}

.mono {
  font-family: var(--font-mono) !important;
  font-variant-numeric: tabular-nums;
}

.accent {
  color: var(--accent) !important;
  font-weight: 700;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .econ-grid-2 {
    grid-template-columns: 1fr;
  }

  .econ-title {
    font-size: 1.5rem;
  }

  .stat-val {
    font-size: 1.1rem;
  }

  .econ-stats-hero {
    grid-template-columns: 1fr;
  }

  .stat-val-hero {
    font-size: 1.5rem;
  }

  .econ-stats {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .col-name {
    min-width: 80px;
  }
}

@media (max-width: 640px) {
  .econ-title { font-size: 1.3rem; }
  .stat-val { font-size: 1rem; }
  .stat-val-hero { font-size: 1.3rem; }
  .econ-stats { grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); }
}
</style>
