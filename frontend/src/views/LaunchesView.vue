<template>
  <div>
    <!-- Editorial Header -->
    <div class="chronicle-header">
      <h1 class="chronicle-title">
        Launch Record
      </h1>
      <p
        v-if="dashStore.data"
        class="chronicle-sub"
      >
        {{ dashStore.data.total_launches.toLocaleString() }} missions ·
        {{ dashStore.data.successful_launches.toLocaleString() }} successful ·
        {{ dashStore.data.success_rate }}% success rate
      </p>
    </div>

    <!-- Chart as THE hero (full width, tall) -->
    <div class="surface chart-hero">
      <span class="section-label">Launches per Year</span>
      <LaunchesByYearChart
        v-if="dashStore.data"
        :data="dashStore.data.launches_by_year"
        :height="360"
      />
      <SkeletonLoader
        v-else
        variant="chart"
        height="360px"
      />
    </div>

    <!-- Vehicle Breakdown -->
    <div
      v-if="dashStore.data"
      class="surface vehicle-section section-gap"
    >
      <span class="section-label">By Vehicle</span>
      <div class="vehicle-list">
        <div
          v-for="item in dashStore.data.launches_by_rocket"
          :key="item.rocket"
          class="vehicle-row"
        >
          <span class="vehicle-name">{{ item.rocket }}</span>
          <div class="vehicle-bar-track">
            <div
              class="vehicle-bar-fill"
              :style="{ width: barWidth(item.count) }"
            />
          </div>
          <span class="vehicle-count">{{ item.count }}</span>
        </div>
      </div>
    </div>

    <!-- Mission Log -->
    <div class="surface mission-log-section section-gap">
      <div class="log-header">
        <span
          class="section-label"
          style="margin-bottom: 0;"
        >Mission Log</span>
        <div class="filters">
          <label
            class="sr-only"
            for="filter-outcome"
          >Filter by outcome</label>
          <select
            id="filter-outcome"
            aria-label="Filter by outcome"
            @change="onSuccessFilter($event.target.value)"
          >
            <option value="">
              All outcomes
            </option>
            <option value="true">
              Successful
            </option>
            <option value="false">
              Failed
            </option>
          </select>
          <label
            class="sr-only"
            for="filter-timeline"
          >Filter by timeline</label>
          <select
            id="filter-timeline"
            aria-label="Filter by timeline"
            @change="onUpcomingFilter($event.target.value)"
          >
            <option value="">
              Past & Upcoming
            </option>
            <option value="false">
              Past only
            </option>
            <option value="true">
              Upcoming only
            </option>
          </select>
          <label
            class="sr-only"
            for="filter-vehicle"
          >Filter by vehicle</label>
          <select
            v-if="rocketsStore.items.length"
            id="filter-vehicle"
            aria-label="Filter by vehicle"
            @change="launchesStore.setFilters({ rocket_id: $event.target.value || null })"
          >
            <option value="">
              All vehicles
            </option>
            <option
              v-for="r in rocketsStore.items"
              :key="r.id"
              :value="r.id"
            >
              {{ r.name }}
            </option>
          </select>
        </div>
      </div>

      <ErrorState
        v-if="launchesStore.error"
        :message="launchesStore.error"
        @retry="launchesStore.load()"
      />
      <SkeletonLoader
        v-else-if="launchesStore.loading"
        variant="table"
        :count="8"
      />

      <DataTable
        v-else
        :columns="columns"
        :rows="launchesStore.items"
        :total="launchesStore.total"
        :page="launchesStore.page"
        :limit="launchesStore.limit"
        :clickable="true"
        @page-change="launchesStore.setPage($event)"
        @row-click="onRowClick"
      >
        <template #name="{ row }">
          <div class="mission-cell">
            <img
              v-if="row.patch_small"
              :src="row.patch_small"
              class="mission-patch"
              :alt="row.name + ' mission patch'"
              width="28"
              height="28"
            >
            <div
              v-else
              class="mission-patch-placeholder"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 2L8 10L4 22L12 18L20 22L16 10L12 2Z"
                  fill="currentColor"
                  opacity="0.35"
                />
                <path
                  d="M12 2L16 10L20 22L12 18L4 22L8 10L12 2Z"
                  stroke="currentColor"
                  stroke-width="1"
                  opacity="0.2"
                  fill="none"
                />
              </svg>
            </div>
            <span>{{ row.name }}</span>
          </div>
        </template>
        <template #success="{ value }">
          <span
            v-if="value !== null && value !== undefined"
            :class="['badge', value ? 'badge-success' : 'badge-error']"
          >
            {{ value ? 'Success' : 'Failed' }}
          </span>
          <span
            v-else
            class="badge badge-neutral"
          >Upcoming</span>
        </template>
        <template #date_utc="{ value }">
          <span class="mono-sm">{{ formatDate(value) }}</span>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatDateShort } from '@/utils/formatDate'
import { useDashboardStore } from '@/stores/dashboard'
import { useRocketsStore } from '@/stores/rockets'
import { useLaunchesStore } from '@/stores/launches'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import DataTable from '@/components/common/DataTable.vue'
import LaunchesByYearChart from '@/components/charts/LaunchesByYearChart.vue'
import type { TableColumn } from '@/types'

const router = useRouter()
const dashStore = useDashboardStore()
const rocketsStore = useRocketsStore()
const launchesStore = useLaunchesStore()

const columns: TableColumn[] = [
  { key: 'name', label: 'Mission' },
  { key: 'date_utc', label: 'Date' },
  { key: 'rocket_name', label: 'Vehicle' },
  { key: 'success', label: 'Outcome' },
]

const maxLaunches = computed((): number => {
  if (!dashStore.data?.launches_by_rocket?.length) return 1
  return Math.max(...dashStore.data.launches_by_rocket.map((d) => d.count))
})

function barWidth(count: number): string { return Math.round((count / maxLaunches.value) * 100) + '%' }
function onSuccessFilter(val: string): void { launchesStore.setFilters({ success: val === '' ? null : val === 'true' }) }
function onUpcomingFilter(val: string): void { launchesStore.setFilters({ upcoming: val === '' ? null : val === 'true' }) }
function onRowClick(row: Record<string, unknown>): void { router.push({ name: 'LaunchDetail', params: { id: row.id as string } }) }

const formatDate = formatDateShort

onMounted(() => {
  if (!dashStore.data) dashStore.load()
  if (!rocketsStore.items.length) rocketsStore.load()
  if (!launchesStore.items.length) launchesStore.load()
})
</script>

<style scoped>
/* === CHRONICLE HEADER === */
.chronicle-header {
  margin-bottom: 16px;
}

.chronicle-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.chronicle-sub {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 6px;
  letter-spacing: 0.02em;
}

/* === CHART HERO === */
.chart-hero {
  margin-bottom: 2px;
}

/* === VEHICLE SECTION === */
.vehicle-section {
  margin-bottom: 2px;
}

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vehicle-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vehicle-name {
  width: 120px;
  font-family: var(--font-display);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}

.vehicle-bar-track {
  flex: 1;
  height: 16px;
  background: var(--chart-track);
  border-radius: 2px;
  overflow: hidden;
}

.vehicle-bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.6s ease;
  opacity: 0.7;
}

.vehicle-count {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  width: 32px;
  text-align: right;
}

/* === MISSION LOG === */
.mission-log-section {
  margin-bottom: 0;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.log-header .filters {
  margin-bottom: 0;
}

/* === TABLE MISSION CELL === */
.mission-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mission-patch {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 2px;
}

.mission-patch-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 2px;
  background: var(--bg-hover);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.mission-patch-placeholder svg {
  width: 14px;
  height: 14px;
}

.mono-sm {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .chronicle-title { font-size: 1.4rem; }
  .chronicle-sub { font-size: 0.85rem; }
  .log-header { flex-direction: column; align-items: flex-start; }
  .vehicle-name { width: 80px; font-size: 0.72rem; }
}

@media (max-width: 640px) {
  .chronicle-title { font-size: 1.2rem; }
  .vehicle-name { width: 60px; font-size: 0.65rem; }
}
</style>
