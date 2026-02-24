<template>
  <div>
    <ErrorState
      v-if="store.error"
      :message="store.error"
      @retry="store.load()"
    />

    <template v-else-if="store.loading && !store.items.length">
      <SkeletonLoader
        variant="rect"
        height="420px"
        rounded="12px"
      />
      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-top: 24px">
        <SkeletonLoader
          variant="stat"
          :count="4"
        />
        <SkeletonLoader
          variant="table"
          :count="6"
        />
      </div>
    </template>

    <template v-else>
      <!-- View header -->
      <div class="view-header">
        <h1 class="view-header-title">
          Starlink Constellation
        </h1>
        <p class="view-header-sub">
          Live tracking of SpaceX's satellite internet network. Click on any satellite in the 3D globe for details, or use the legend to filter by version.
        </p>
      </div>

      <!-- Globe Hero with overlay metrics -->
      <div class="globe-hero surface">
        <StarlinkGlobe
          :positions="positions"
          :active-versions="activeVersions"
          :selected-sat="selectedSatellite"
          :version-color-map="versionColorMap"
          @visible-count="visibleCount = $event"
          @satellite-click="onSatelliteClick"
        />

        <!-- Overlay metrics -->
        <div
          v-if="stats"
          class="globe-overlay"
        >
          <div class="overlay-metric overlay-left">
            <span class="overlay-value">{{ stats.total.toLocaleString() }}</span>
            <span class="overlay-label">Satellites Tracked</span>
            <span class="human-context">Providing internet to 100+ countries</span>
          </div>
          <div class="overlay-metric overlay-right">
            <span class="overlay-value">{{ stats.avg_height_km }} <small>km</small></span>
            <span class="overlay-label">Avg Altitude</span>
            <span class="human-context">~{{ Math.round(stats.avg_height_km / 11) }}&times; higher than a commercial airplane</span>
          </div>

          <!-- Interactive Legend -->
          <div
            v-if="versionLegend.length"
            class="globe-legend overlay-metric"
          >
            <button
              v-for="item in versionLegend"
              :key="item.version"
              class="legend-item"
              :class="{ dimmed: !item.active }"
              @click="toggleVersion(item.version)"
            >
              <span
                class="legend-dot"
                :style="{ background: item.color }"
              />
              <span class="legend-name">{{ item.version || 'Unknown' }}</span>
            </button>
          </div>

          <!-- Satellite Detail Card -->
          <Transition name="sat-detail">
            <div
              v-if="selectedSatellite"
              key="detail"
              class="sat-detail"
            >
              <button
                class="sat-detail-close"
                aria-label="Close satellite details"
                @click="selectedSatellite = null"
              >
                &times;
              </button>
              <div
                v-if="selectedSatellite.object_name"
                class="sat-detail-name"
              >
                {{ selectedSatellite.object_name }}
              </div>
              <div class="sat-detail-header">
                <span
                  class="sat-detail-dot"
                  :style="{ background: getVersionColor(selectedSatellite.version) }"
                />
                <span class="sat-detail-version">{{ selectedSatellite.version || 'Unknown' }}</span>
              </div>
              <div class="sat-detail-rows">
                <div class="sat-detail-row">
                  <span class="sat-detail-label">Latitude</span>
                  <span class="sat-detail-value">{{ selectedSatellite.latitude.toFixed(4) }}°</span>
                </div>
                <div class="sat-detail-row">
                  <span class="sat-detail-label">Longitude</span>
                  <span class="sat-detail-value">{{ selectedSatellite.longitude.toFixed(4) }}°</span>
                </div>
                <div class="sat-detail-row">
                  <span class="sat-detail-label">Altitude</span>
                  <span class="sat-detail-value">{{ selectedSatellite.height_km ? selectedSatellite.height_km.toLocaleString() + ' km' : '—' }}</span>
                </div>
                <div class="sat-detail-row">
                  <span class="sat-detail-label">
                    Velocity
                    <InfoTip>Kilometers per second. At this speed, the satellite orbits Earth in about 90 minutes.</InfoTip>
                  </span>
                  <span class="sat-detail-value">{{ selectedSatellite.velocity_kms ? selectedSatellite.velocity_kms.toFixed(2) + ' km/s' : '—' }}</span>
                </div>
              </div>
            </div>
          </Transition>

          <div class="overlay-metric overlay-bottom">
            <span class="overlay-label">
              {{ visibleCount.toLocaleString() }} of {{ positions.length.toLocaleString() }} visible · click satellite for details
            </span>
          </div>
        </div>
      </div>

      <!-- Satellites by Version -->
      <div
        v-if="stats && stats.by_version.length"
        class="surface"
        style="margin-bottom: 0;"
      >
        <span class="section-label">Satellites by Version</span>
        <div class="version-list">
          <div
            v-for="ver in stats.by_version"
            :key="ver.version"
            class="version-row"
          >
            <span
              class="version-dot-lg"
              :style="{ background: versionColorMap[ver.version] }"
            />
            <span class="version-name">{{ ver.version || 'Unknown' }}</span>
            <div class="version-bar-track">
              <div
                class="version-bar-fill"
                :style="{ width: versionBarWidth(ver.count), background: versionColorMap[ver.version] }"
              />
            </div>
            <span class="version-pct">{{ ((ver.count / stats.total) * 100).toFixed(1) }}%</span>
            <span class="version-count">{{ ver.count.toLocaleString() }}</span>
          </div>
        </div>
      </div>

      <!-- Satellite Registry -->
      <div
        class="surface"
        style="margin-top: 2px;"
      >
        <span class="section-label">Satellite Registry</span>
        <DataTable
          :columns="columns"
          :rows="store.items"
          :total="store.total"
          :page="store.page"
          :limit="store.limit"
          @page-change="store.setPage($event)"
        >
          <template #object_name="{ row, value }">
            <div class="sat-cell">
              <span class="sat-name">{{ value || 'Unknown' }}</span>
              <span class="sat-id">{{ row.id }}</span>
            </div>
          </template>
          <template #version="{ value }">
            <span
              v-if="value"
              class="badge badge-neutral version-badge"
            >
              <span
                class="version-dot"
                :style="{ background: getVersionColor(value) }"
              />
              {{ value }}
            </span>
            <span
              v-else
              class="text-muted"
            >—</span>
          </template>
          <template #height_km="{ value }">
            <span
              v-if="value"
              class="mono"
            >{{ value.toLocaleString() }} <small class="unit">km</small></span>
            <span
              v-else
              class="text-muted"
            >—</span>
          </template>
          <template #velocity_kms="{ value }">
            <span
              v-if="value"
              class="mono"
            >{{ value.toFixed(2) }} <small class="unit">km/s</small></span>
            <span
              v-else
              class="text-muted"
            >—</span>
          </template>
          <template #latitude="{ row }">
            <span
              v-if="row.latitude != null && row.longitude != null"
              class="mono coords"
            >{{ row.latitude.toFixed(2) }}°, {{ row.longitude.toFixed(2) }}°</span>
            <span
              v-else
              class="text-muted"
            >—</span>
          </template>
        </DataTable>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStarlinkStore } from '@/stores/starlink'
import { fetchStarlinkStats, fetchStarlinkPositions } from '@/api'
import { getCssVar } from '@/utils/chartColors'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import DataTable from '@/components/common/DataTable.vue'
import StarlinkGlobe from '@/components/charts/StarlinkGlobe.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import type { StarlinkStats, StarlinkPosition, TableColumn } from '@/types'

const store = useStarlinkStore()
const stats = ref<StarlinkStats | null>(null)
const positions = ref<StarlinkPosition[]>([])
const visibleCount = ref(0)
const activeVersions = ref<Set<string>>(new Set())
const selectedSatellite = ref<StarlinkPosition | null>(null)

function onSatelliteClick(sat: StarlinkPosition | null): void {
  selectedSatellite.value = sat || null
}

const CSS_COLOR_VARS = ['--accent', '--accent-blue', '--accent-cyan', '--success', '--warning', '--text-secondary']

function getColorPalette(): string[] {
  return CSS_COLOR_VARS.map((v) => getCssVar(v))
}

const columns: TableColumn[] = [
  { key: 'object_name', label: 'Satellite' },
  { key: 'version', label: 'Version' },
  { key: 'height_km', label: 'Altitude' },
  { key: 'velocity_kms', label: 'Velocity' },
  { key: 'latitude', label: 'Position' },
]

const versionColorMap = computed((): Record<string, string> => {
  if (!stats.value?.by_version) return {}
  const palette = getColorPalette()
  const map: Record<string, string> = {}
  stats.value.by_version.forEach((v, i) => {
    const key = v.version ?? 'unknown'
    map[key] = palette[i % palette.length]
  })
  return map
})

interface VersionLegendItem {
  version: string | null
  count: number
  color: string
  active: boolean
}

const versionLegend = computed((): VersionLegendItem[] => {
  if (!stats.value?.by_version) return []
  return stats.value.by_version.map((v) => ({
    version: v.version,
    count: v.count,
    color: versionColorMap.value[v.version ?? 'unknown'] || getCssVar('--text-muted'),
    active: activeVersions.value.size === 0 || activeVersions.value.has(v.version ?? 'unknown'),
  }))
})

function toggleVersion(version: string): void {
  const next = new Set(activeVersions.value)
  if (next.size === 0) {
    next.clear()
    next.add(version)
  } else if (next.has(version)) {
    next.delete(version)
    if (next.size === 0) {
      activeVersions.value = new Set()
      return
    }
  } else {
    next.add(version)
    const allVersions = stats.value?.by_version?.map((v) => v.version ?? 'unknown') || []
    if (allVersions.every((v) => next.has(v))) {
      activeVersions.value = new Set()
      return
    }
  }
  activeVersions.value = next
}

function versionBarWidth(count: number): string {
  if (!stats.value) return '0%'
  return Math.round((count / stats.value.total) * 100) + '%'
}

function getVersionColor(versionName: string | null): string {
  if (!stats.value?.by_version) return getCssVar('--text-muted')
  const idx = stats.value.by_version.findIndex((v) => v.version === versionName)
  if (idx === -1) return getCssVar('--text-muted')
  const palette = getColorPalette()
  return palette[idx % palette.length]
}

async function loadStats(): Promise<void> {
  try { stats.value = await fetchStarlinkStats() } catch { /* optional */ }
}

async function loadPositions(): Promise<void> {
  try { positions.value = await fetchStarlinkPositions() } catch { /* optional */ }
}

onMounted(() => {
  if (!store.items.length) store.load()
  loadStats()
  loadPositions()
})
</script>

<style scoped>
/* === GLOBE HERO === */
.globe-hero {
  position: relative;
  padding: 0;
  margin-bottom: 2px;
  overflow: hidden;
}

.globe-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  padding: 24px 28px;
}

.overlay-metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: var(--radius);
  background: var(--bg-surface);
  opacity: 0.92;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  align-self: flex-start;
}

.overlay-left {
  align-self: flex-end;
}

.overlay-right {
  align-self: flex-end;
}

.overlay-bottom {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  white-space: nowrap;
}

.overlay-value {
  font-family: var(--font-mono);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
  letter-spacing: -0.02em;
}

.overlay-value small {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.overlay-label {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* === INTERACTIVE LEGEND === */
.globe-legend {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: row;
  gap: 2px;
  padding: 6px 10px;
  pointer-events: auto;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 3px;
  transition: opacity 0.15s, background 0.15s;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.legend-item:hover {
  background: var(--bg-hover);
}

.legend-item.dimmed {
  opacity: 0.25;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  white-space: nowrap;
}

/* === SATELLITE DETAIL CARD === */
.sat-detail {
  position: absolute;
  bottom: 60px;
  right: 28px;
  padding: 16px 20px;
  min-width: 220px;
  pointer-events: auto;
  z-index: 10;
  border-radius: var(--radius);
  background: var(--bg-surface);
  opacity: 1;
  border: 1px solid var(--border);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
}

.sat-detail-close {
  position: absolute;
  top: 8px;
  right: 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
  padding: 2px 4px;
  transition: color 0.15s;
}

.sat-detail-close:hover {
  color: var(--text);
}

.sat-detail-name {
  font-family: var(--font-mono);
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
  margin-bottom: 6px;
  padding-right: 20px;
}

.sat-detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.sat-detail-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sat-detail-version {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.sat-detail-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sat-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.sat-detail-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.sat-detail-value {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text);
}

/* Transition */
.sat-detail-enter-active,
.sat-detail-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.sat-detail-enter-from,
.sat-detail-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* === VERSION LIST === */
.version-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.version-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.version-dot-lg {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.version-name {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  color: var(--text-secondary);
  width: 70px;
  flex-shrink: 0;
}

.version-bar-track {
  flex: 1;
  height: 14px;
  background: var(--chart-track);
  border-radius: 2px;
  overflow: hidden;
}

.version-bar-fill {
  height: 100%;
  border-radius: 2px;
  opacity: 0.65;
  transition: width 0.5s ease;
}

.version-pct {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-muted);
  width: 48px;
  text-align: right;
  flex-shrink: 0;
}

.version-count {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  width: 55px;
  text-align: right;
  flex-shrink: 0;
}

/* === TABLE VERSION BADGE === */
.version-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.version-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* === SATELLITE CELL === */
.sat-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sat-name {
  font-family: var(--font-mono);
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.01em;
}

.sat-id {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

/* === UTILITIES === */
.mono {
  font-family: var(--font-mono);
  font-size: 0.82rem;
}

.unit {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 400;
}

.coords {
  font-size: 0.78rem;
  color: var(--text-secondary);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .overlay-value { font-size: 1.3rem; }
  .overlay-label { font-size: 0.7rem; }
  .overlay-metric { padding: 8px 12px; }
  .globe-overlay { padding: 16px; }
  .globe-legend { flex-wrap: wrap; justify-content: center; }
  .legend-item { font-size: 0.65rem; padding: 3px 6px; }
  .sat-detail {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    top: auto;
    width: 100%;
    min-width: auto;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-height: 50vh;
    overflow-y: auto;
  }
  .version-name { width: auto; min-width: 50px; font-size: 0.78rem; }
}

@media (max-width: 640px) {
  .overlay-value { font-size: 1.1rem; }
  .overlay-metric { padding: 6px 10px; }
  .globe-overlay { padding: 12px; }
  .overlay-bottom { white-space: normal; text-align: center; }
}
</style>
