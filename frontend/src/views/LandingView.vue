<template>
  <section class="landing-page">
    <header class="landing-header">
      <span class="header-tag">RECOVERY</span>
      <h1>Landing Operations</h1>
      <p
        v-if="data"
        class="header-sub"
      >
        Propulsive landing is what makes SpaceX rockets reusable
      </p>
    </header>

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
        variant="rect"
        height="300px"
      />
      <SkeletonLoader
        variant="table"
        :count="4"
      />
    </div>

    <template v-else-if="data">
      <!-- Hero Stats -->
      <div class="stats-grid">
        <div class="stat-card surface">
          <span class="stat-label">Total Attempts (all-time)</span>
          <span class="stat-value">{{ data.stats.total_attempts }}</span>
        </div>
        <div class="stat-card surface">
          <span class="stat-label">Total Successes</span>
          <span class="stat-value accent">{{ data.stats.total_successes }}</span>
        </div>
        <div class="stat-card surface">
          <span class="stat-label">Overall Rate</span>
          <span class="stat-value">{{ data.stats.overall_success_rate }}%</span>
        </div>
      </div>

      <!-- RTLS vs ASDS comparison -->
      <div class="comparison-row">
        <div class="compare-card surface">
          <div class="compare-header">
            <span class="compare-badge rtls">RTLS</span>
            <span class="compare-title">Return to Launch Site</span>
          </div>
          <div class="compare-stats">
            <div class="compare-stat">
              <span class="cs-value">{{ data.stats.rtls_successes }}</span>
              <span class="cs-label">Successes</span>
            </div>
            <div class="compare-stat">
              <span class="cs-value">{{ data.stats.rtls_attempts }}</span>
              <span class="cs-label">Attempts</span>
            </div>
            <div class="compare-stat">
              <span class="cs-value">{{ rtlsRate }}%</span>
              <span class="cs-label">Rate</span>
            </div>
          </div>
          <div class="compare-bar-track">
            <div
              class="compare-bar rtls-bar"
              :style="{ width: rtlsRate + '%' }"
            />
          </div>
        </div>

        <div class="compare-card surface">
          <div class="compare-header">
            <span class="compare-badge asds">ASDS</span>
            <span class="compare-title">Autonomous Spaceport Drone Ship</span>
          </div>
          <div class="compare-stats">
            <div class="compare-stat">
              <span class="cs-value">{{ data.stats.asds_successes }}</span>
              <span class="cs-label">Successes</span>
            </div>
            <div class="compare-stat">
              <span class="cs-value">{{ data.stats.asds_attempts }}</span>
              <span class="cs-label">Attempts</span>
            </div>
            <div class="compare-stat">
              <span class="cs-value">{{ asdsRate }}%</span>
              <span class="cs-label">Rate</span>
            </div>
          </div>
          <div class="compare-bar-track">
            <div
              class="compare-bar asds-bar"
              :style="{ width: asdsRate + '%' }"
            />
          </div>
        </div>
      </div>

      <!-- Map -->
      <div class="section-block surface">
        <h2 class="section-title">
          Landing Zones
        </h2>
        <LandingMapChart :landpads="data.landpads" />
        <div class="map-legend">
          <span class="legend-item"><span class="legend-dot rtls-dot" /> RTLS</span>
          <span class="legend-item">
            <svg
              class="legend-diamond"
              viewBox="0 0 12 12"
              width="10"
              height="10"
            >
              <path
                d="M6,1 L10.5,6 L6,11 L1.5,6 Z"
                fill="var(--accent-blue)"
              />
            </svg>
            ASDS
          </span>
          <span class="legend-note">Hover over markers for landing details</span>
        </div>
      </div>

      <!-- Landpads Table -->
      <div class="section-block surface">
        <h2 class="section-title">
          All Landing Pads
        </h2>
        <div class="table-wrap">
          <table class="pads-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Location</th>
                <th class="num">
                  Attempts
                </th>
                <th class="num">
                  Successes
                </th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="pad in data.landpads"
                :key="pad.id"
              >
                <td class="pad-name">
                  {{ pad.full_name }}
                </td>
                <td>
                  <span
                    class="type-badge"
                    :class="pad.type.toLowerCase()"
                  >{{ pad.type }}</span>
                </td>
                <td>
                  <span
                    class="status-badge"
                    :class="pad.status"
                  >{{ pad.status }}</span>
                </td>
                <td class="pad-loc">
                  {{ pad.locality || '—' }}{{ pad.region ? ', ' + pad.region : '' }}
                </td>
                <td class="num">
                  {{ pad.landing_attempts }}
                </td>
                <td class="num">
                  {{ pad.landing_successes }}
                </td>
                <td>
                  <div class="rate-cell">
                    <div class="rate-bar-track">
                      <div
                        class="rate-bar"
                        :class="pad.type.toLowerCase()"
                        :style="{ width: pad.success_rate + '%' }"
                      />
                    </div>
                    <span class="rate-value">{{ pad.success_rate }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <ErrorState
      v-else
      message="Unable to load landing data."
      @retry="loadData"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fetchLanding } from '@/api'
import LandingMapChart from '@/components/charts/LandingMapChart.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import type { LandingResponse } from '@/types'

const data = ref<LandingResponse | null>(null)
const loading = ref(true)

async function loadData(): Promise<void> {
  loading.value = true
  data.value = null
  try {
    data.value = await fetchLanding()
  } catch (e) {
    console.error('Failed to fetch landing data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

const rtlsRate = computed((): number => {
  if (!data.value) return 0
  const { rtls_attempts, rtls_successes } = data.value.stats
  return rtls_attempts ? Math.round((rtls_successes / rtls_attempts) * 1000) / 10 : 0
})

const asdsRate = computed((): number => {
  if (!data.value) return 0
  const { asds_attempts, asds_successes } = data.value.stats
  return asds_attempts ? Math.round((asds_successes / asds_attempts) * 1000) / 10 : 0
})
</script>

<style scoped>
.landing-page {
  max-width: 1080px;
  margin: 0 auto;
}

.landing-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-tag {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--accent);
  letter-spacing: 0.14em;
  display: block;
  margin-bottom: 8px;
}

.landing-header h1 {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 8px;
}

.header-sub {
  font-size: 1.05rem;
  color: var(--text-secondary);
  margin: 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 6px;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
}

.stat-value.accent {
  color: var(--accent);
}

/* Comparison */
.comparison-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 28px;
}

.compare-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px;
}

.compare-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.compare-badge {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 3px 8px;
  border-radius: 4px;
}

.compare-badge.rtls {
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  color: var(--accent);
}

.compare-badge.asds {
  background: color-mix(in srgb, var(--accent-blue) 18%, transparent);
  color: var(--accent-blue);
}

.compare-title {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.compare-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.compare-stat {
  display: flex;
  flex-direction: column;
}

.cs-value {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text);
}

.cs-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.compare-bar-track {
  height: 6px;
  background: var(--chart-track);
  border-radius: 3px;
  overflow: hidden;
}

.compare-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.rtls-bar { background: var(--accent); }
.asds-bar { background: var(--accent-blue); }

/* Sections */
.section-block {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 28px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 16px;
}

.map-legend {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.rtls-dot { background: var(--accent); }

.legend-diamond {
  flex-shrink: 0;
}

.legend-note {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-left: auto;
}

/* Table */
.table-wrap {
  overflow-x: auto;
}

.pads-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.pads-table th {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-strong);
}

.pads-table th.num,
.pads-table td.num {
  text-align: right;
}

.pads-table td {
  padding: 10px 12px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.pad-name {
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
}

.pad-loc {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.type-badge {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 7px;
  border-radius: 4px;
}

.type-badge.rtls {
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  color: var(--accent);
}

.type-badge.asds {
  background: color-mix(in srgb, var(--accent-blue) 18%, transparent);
  color: var(--accent-blue);
}

.status-badge {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: capitalize;
}

.status-badge.active {
  background: color-mix(in srgb, var(--success) 15%, transparent);
  color: var(--success);
}

.status-badge.retired {
  background: color-mix(in srgb, var(--text-muted) 15%, transparent);
  color: var(--text-muted);
}

.status-badge.under.construction,
.status-badge.under_construction {
  background: color-mix(in srgb, var(--warning) 15%, transparent);
  color: var(--warning);
}

.rate-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rate-bar-track {
  flex: 1;
  height: 5px;
  background: var(--chart-track);
  border-radius: 3px;
  overflow: hidden;
  min-width: 60px;
}

.rate-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.rate-bar.rtls { background: var(--accent); }
.rate-bar.asds { background: var(--accent-blue); }

.rate-value {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text);
  min-width: 42px;
  text-align: right;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .comparison-row { grid-template-columns: 1fr; }
  .landing-page { padding: 0; }
  .landing-header h1 { font-size: 1.8rem; }
  .pads-table { font-size: 0.78rem; }
  .pads-table th { font-size: 0.65rem; padding: 6px 8px; }
  .pads-table td { padding: 8px; }
  .pad-name { white-space: normal; }
}

@media (max-width: 640px) {
  .landing-page { padding: 0; }
  .landing-header h1 { font-size: 1.4rem; }
  .stat-value { font-size: 1.6rem; }
}
</style>
