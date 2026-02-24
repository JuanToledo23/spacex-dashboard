<template>
  <div>
    <ErrorState
      v-if="store.error"
      :message="store.error"
      @retry="store.load()"
    />

    <template v-else-if="store.loading">
      <SkeletonLoader
        variant="hero"
        height="280px"
      />
      <div
        class="bento-stats"
        style="margin-top: 8px"
      >
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <div class="skeleton-row">
        <div style="flex: 1; min-width: 0">
          <SkeletonLoader
            variant="chart"
            height="320px"
          />
        </div>
      </div>
    </template>

    <template v-else-if="store.data">
      <!-- View header -->
      <div class="view-header">
        <h1 class="view-header-title">
          Mission Control
        </h1>
        <p class="view-header-sub">
          Real-time snapshot of SpaceX mission activity, success metrics, and launch frequency.
        </p>
      </div>

      <!-- HERO: Latest Mission (full width) -->
      <div class="bento-hero image-hero latest-card">
        <div
          v-if="heroImage"
          class="image-hero-bg"
          :style="{ backgroundImage: `url(${heroImage})` }"
        />
        <div class="image-hero-content">
          <span class="hero-label latest-label"><span class="latest-pulse" /> Latest Mission</span>
          <div class="hero-row">
            <img
              v-if="store.data.latest_launch?.patch_small"
              :src="store.data.latest_launch.patch_small"
              class="hero-patch"
              alt="Mission patch"
              width="100"
              height="100"
            >
            <div class="hero-text">
              <h1 class="hero-name">
                {{ store.data.latest_launch?.name || 'SpaceX' }}
              </h1>
              <div
                v-if="store.data.latest_launch"
                class="hero-meta"
              >
                <span v-if="store.data.latest_launch.rocket_name">{{ store.data.latest_launch.rocket_name }}</span>
                <span class="sep">·</span>
                <span>{{ formatDate(store.data.latest_launch.date_utc) }}</span>
                <span class="sep">·</span>
                <span :class="store.data.latest_launch.success ? 'text-success' : 'text-error'">
                  {{ store.data.latest_launch.success ? 'SUCCESS' : store.data.latest_launch.upcoming ? 'UPCOMING' : 'FAILED' }}
                </span>
              </div>
              <p
                v-if="store.data.latest_launch?.details"
                class="hero-details"
              >
                {{ store.data.latest_launch.details }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- KEY STATS ROW (full width, horizontal) -->
      <div class="bento-stats">
        <div class="stat-cell surface-dense">
          <span class="stat-value">{{ store.data.total_launches.toLocaleString() }}</span>
          <span class="stat-name">Missions</span>
          <span class="human-context">Since 2006</span>
        </div>
        <div class="stat-cell surface-dense">
          <span class="stat-value text-success">{{ store.data.success_rate }}%</span>
          <span class="stat-name">Success Rate</span>
          <span class="human-context">Higher than most commercial launch providers</span>
        </div>
        <div class="stat-cell surface-dense">
          <span class="stat-value">{{ store.data.total_landings.toLocaleString() }}</span>
          <span class="stat-name">Booster Landings</span>
          <span class="human-context">Each saves ~$50M in hardware</span>
        </div>
      </div>

      <!-- ROW 2: Launch Cadence (full width) -->
      <div class="section-block surface section-gap">
        <span class="section-label">Launch Cadence</span>
        <LaunchCadenceChart :data="store.data.launches_by_year" />
      </div>

      <!-- ROW 3: Next Mission + Recent | Launch Sites -->
      <div class="bottom-grid section-gap">
        <div class="bottom-left">
          <div
            v-if="store.data.next_launch"
            class="surface next-card"
            style="margin-bottom: 2px;"
          >
            <span class="section-label next-label"><span class="next-pulse" /> Next Mission</span>
            <div class="next-block">
              <img
                v-if="store.data.next_launch.patch_small"
                :src="store.data.next_launch.patch_small"
                class="next-patch"
                alt="Next mission patch"
                width="48"
                height="48"
              >
              <div
                v-else
                class="next-patch-placeholder"
              >
                <svg
                  viewBox="0 0 48 48"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <circle
                    cx="24"
                    cy="24"
                    r="23"
                    stroke="currentColor"
                    stroke-width="1"
                    opacity="0.25"
                  />
                  <path
                    d="M24 8 L28 20 L24 38 L20 20 Z"
                    fill="currentColor"
                    opacity="0.35"
                  />
                  <path
                    d="M16 26 L20 20 L24 24 Z"
                    fill="currentColor"
                    opacity="0.2"
                  />
                  <path
                    d="M32 26 L28 20 L24 24 Z"
                    fill="currentColor"
                    opacity="0.2"
                  />
                </svg>
              </div>
              <div>
                <p class="next-name">
                  {{ store.data.next_launch.name }}
                </p>
                <p class="next-meta">
                  <span v-if="store.data.next_launch.rocket_name">{{ store.data.next_launch.rocket_name }}</span>
                  <span
                    v-if="store.data.next_launch.rocket_name"
                    class="sep"
                  >·</span>
                  <span>{{ formatDate(store.data.next_launch.date_utc) }}</span>
                </p>
              </div>
            </div>
          </div>
          <div class="surface">
            <span class="section-label">Recent Missions</span>
            <MiniTimeline :items="store.data.recent_launches" />
          </div>
        </div>
        <div class="bottom-right surface">
          <div class="launch-sites-section">
            <div class="ls-header">
              <span class="section-label">Launch Sites</span>
              <span class="ls-total">{{ totalSiteLaunches }} missions</span>
            </div>
            <div class="stacked-bar">
              <div
                v-for="(site, idx) in store.data.launches_by_site"
                :key="site.site"
                class="stacked-seg"
                :style="{ flex: site.count, background: siteColors[idx] }"
                :title="`${site.site} — ${site.count} launches (${Math.round(site.count / totalSiteLaunches * 100)}%)`"
              />
            </div>
            <div class="stacked-legend">
              <div
                v-for="(site, idx) in store.data.launches_by_site"
                :key="'leg-' + site.site"
                class="stacked-legend-item"
              >
                <span
                  class="stacked-dot"
                  :style="{ background: siteColors[idx] }"
                />
                <span class="stacked-label">{{ site.site }}</span>
                <span class="stacked-val">{{ site.count }}</span>
                <span class="stacked-pct">{{ Math.round(site.count / totalSiteLaunches * 100) }}%</span>
              </div>
            </div>
          </div>

          <div
            v-if="store.data.launchpads?.length"
            class="site-performance"
          >
            <div class="site-perf-header">
              <span class="section-label">Site Performance</span>
              <span class="site-perf-subtitle">Success Rate</span>
            </div>
            <div
              v-for="pad in store.data.launchpads"
              :key="pad.id"
              class="site-row"
            >
              <div class="site-top">
                <span class="site-name">{{ pad.full_name }}</span>
                <span
                  class="site-status"
                  :class="'status-' + pad.status"
                >{{ pad.status }}</span>
              </div>
              <div
                v-if="pad.locality || pad.region"
                class="site-location"
              >
                {{ pad.locality }}<span v-if="pad.locality && pad.region">, </span>{{ pad.region }}
              </div>
              <div class="site-bottom">
                <div class="site-bar-track">
                  <div
                    class="site-bar-fill"
                    :style="{ width: siteSuccessRate(pad) + '%' }"
                  />
                </div>
                <span class="site-rate">{{ siteSuccessRate(pad) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ROW 4: Recommended Actions -->
      <div
        class="highlights-section section-gap"
        :class="{ 'highlights-ai': isAiInsights }"
      >
        <div class="highlights-header">
          <div class="highlights-title-row">
            <span class="section-label">Recommended Actions</span>
            <span
              v-if="isAiInsights"
              class="highlights-ai-tag"
            >
              <svg
                class="sparkle-icon"
                viewBox="0 0 16 16"
                width="12"
                height="12"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M8 0l1.5 5.2L14 6l-4 3.3 1.2 5.2L8 11.8l-3.2 2.7L6 9.3 2 6l4.5-.8z" />
              </svg>
              Smart Actions
            </span>
          </div>
          <p
            v-if="isAiInsights"
            class="highlights-sub"
          >
            Cross-domain recommendations orchestrated from real-time SpaceX data
          </p>
        </div>

        <div class="highlights-grid">
          <div
            v-for="insight in store.data.insights"
            :key="insight.id"
            class="highlight-card surface-dense"
          >
            <div class="hc-top">
              <span
                class="hc-action-icon"
                :class="'icon-' + (insight.action_type || 'monitor')"
                :title="actionLabel(insight.action_type)"
              >
                <svg
                  viewBox="0 0 16 16"
                  width="14"
                  height="14"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  aria-hidden="true"
                >
                  <path :d="actionPath(insight.action_type)" />
                </svg>
              </span>
              <span class="hc-action-label">{{ actionLabel(insight.action_type) }}</span>
              <span
                v-if="insight.priority"
                class="hc-priority"
                :class="'priority-' + insight.priority"
              >{{ insight.priority }}</span>
            </div>
            <p class="highlight-text">
              {{ insight.text }}
            </p>
            <div
              v-if="insight.domains && insight.domains.length"
              class="hc-domains"
            >
              <span
                v-for="domain in insight.domains"
                :key="domain"
                class="hc-domain-pill"
              >{{ domain }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { formatDateShort } from '@/utils/formatDate'
import { useDashboardStore } from '@/stores/dashboard'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import MiniTimeline from '@/components/common/MiniTimeline.vue'
import LaunchCadenceChart from '@/components/charts/LaunchCadenceChart.vue'
import type { LaunchpadSummary } from '@/types'

const store = useDashboardStore()

const siteColors: string[] = [
  'var(--accent)',
  'var(--accent-blue)',
  'var(--accent-cyan)',
  'var(--text-secondary)',
  'var(--warning)',
  'var(--success)',
]

const isAiInsights = computed((): boolean => {
  if (!store.data?.insights?.length) return false
  return store.data.insights.some(i => i.type === 'ai_summary')
})

const heroImage = computed((): string | null => {
  const images = store.data?.latest_launch?.flickr_images || []
  return images.length > 0 ? images[0] : null
})

const totalSiteLaunches = computed((): number => {
  if (!store.data?.launches_by_site) return 0
  return store.data.launches_by_site.reduce((s, d) => s + d.count, 0)
})

function siteSuccessRate(pad: LaunchpadSummary): number {
  if (!pad.launch_attempts) return 0
  return Math.round((pad.launch_successes / pad.launch_attempts) * 100)
}

const formatDate = formatDateShort

const actionIcons: Record<string, string> = {
  optimize: 'M8 2v4M8 10v4M2 8h4M10 8h4',
  investigate: 'M11 11l4 4M7 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z',
  scale: 'M8 14V2M4 6l4-4 4 4',
  reduce: 'M8 2v12M4 10l4 4 4-4',
  monitor: 'M1 8h2l2-4 3 8 2-5 2 3h3',
}

const actionLabels: Record<string, string> = {
  optimize: 'Optimize',
  investigate: 'Investigate',
  scale: 'Scale',
  reduce: 'Reduce',
  monitor: 'Monitor',
}

function actionPath(type?: string | null): string {
  return actionIcons[type || 'monitor'] || actionIcons.monitor
}

function actionLabel(type?: string | null): string {
  return actionLabels[type || 'monitor'] || 'Monitor'
}

onMounted(() => {
  if (!store.data) store.load()
})
</script>

<style scoped>
/* === SKELETON === */
.skeleton-row {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  flex-wrap: wrap;
}

/* === BENTO GRID: Hero + Stats === */
.bento-hero {
  min-height: 240px;
  border-radius: var(--radius-lg);
}

.bento-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  margin-top: 8px;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 16px 10px;
  gap: 4px;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
  letter-spacing: -0.02em;
}

.stat-value.accent { color: var(--accent); }

.stat-name {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* === LATEST MISSION CARD === */
.latest-card {
  border-left: 4px solid var(--success);
  position: relative;
}

.latest-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, color-mix(in srgb, var(--success) 10%, transparent) 0%, transparent 50%);
  z-index: 0;
  border-radius: inherit;
  pointer-events: none;
}

.latest-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.latest-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  display: inline-block;
  animation: pulse-latest 2.5s ease-in-out infinite;
}

@keyframes pulse-latest {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 var(--success); }
  50% { opacity: 0.6; box-shadow: 0 0 0 5px transparent; }
}

/* === HERO CONTENT === */
.hero-label {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--accent);
  margin-bottom: 12px;
  display: block;
}

.latest-card .hero-label {
  color: var(--success);
}

.hero-row {
  display: flex;
  align-items: center;
  gap: 24px;
}

.hero-text {
  flex: 1;
  min-width: 0;
}

.hero-name {
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text);
  text-transform: uppercase;
  line-height: 1.1;
  letter-spacing: 0.02em;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.sep { color: var(--text-muted); }
.text-success { color: var(--success); }
.text-error { color: var(--error); }

.hero-details {
  margin-top: 10px;
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 480px;
}

.hero-patch {
  width: 100px;
  height: 100px;
  object-fit: contain;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 12px rgba(0,0,0,0.4));
}

/* === SECTION BLOCK === */
.section-block {
  border-radius: var(--radius);
}

/* === BOTTOM GRID === */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  margin-top: 2px;
}

.bottom-left {
  display: flex;
  flex-direction: column;
}

.bottom-left .surface:last-child {
  flex: 1;
}

.bottom-right {
  display: flex;
  flex-direction: column;
}

/* === LAUNCH SITES STACKED BAR === */
.launch-sites-section {
  margin-bottom: 16px;
}

.ls-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 12px;
}

.ls-total {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-muted);
}

.stacked-bar {
  display: flex;
  height: 28px;
  border-radius: 4px;
  overflow: hidden;
  gap: 2px;
}

.stacked-seg {
  transition: filter 0.15s, flex 0.5s ease;
  cursor: default;
  min-width: 4px;
}

.stacked-seg:first-child {
  border-radius: 4px 0 0 4px;
}

.stacked-seg:last-child {
  border-radius: 0 4px 4px 0;
}

.stacked-seg:hover {
  filter: brightness(1.2);
}

.stacked-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  margin-top: 12px;
}

.stacked-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stacked-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}

.stacked-label {
  color: var(--text);
  font-weight: 500;
}

.stacked-val {
  font-weight: 700;
  color: var(--text);
}

.stacked-pct {
  color: var(--text-muted);
  font-size: 0.68rem;
}

/* === SITE PERFORMANCE === */
.site-performance {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0;
}

.site-perf-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.site-perf-header .section-label {
  margin-bottom: 0;
}

.site-perf-subtitle {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.site-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.site-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.site-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.site-name {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text);
  flex: 1;
  min-width: 0;
}

.site-location {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 1px;
  margin-bottom: 2px;
}

.site-bottom {
  display: flex;
  align-items: center;
  gap: 10px;
}

.site-bar-track {
  flex: 1;
  height: 8px;
  background: var(--chart-track);
  border-radius: 2px;
  overflow: hidden;
}

.site-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--success);
  opacity: 0.7;
  transition: width 0.5s ease;
}

.site-rate {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text);
  width: 36px;
  text-align: right;
  flex-shrink: 0;
}

.site-status {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  border-radius: 3px;
  flex-shrink: 0;
  line-height: 1.2;
}

.status-active {
  color: var(--success);
  background: color-mix(in srgb, var(--success) 14%, transparent);
}

.status-retired {
  color: var(--text-muted);
  background: var(--chart-track);
}

.status-under_construction {
  color: var(--warning);
  background: color-mix(in srgb, var(--warning) 14%, transparent);
}

/* === NEXT MISSION === */
.next-card {
  border-left: 4px solid var(--accent);
  background: linear-gradient(135deg, var(--accent-dim) 0%, transparent 60%), var(--bg-surface);
  position: relative;
}

.next-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.next-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  display: inline-block;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 var(--accent); }
  50% { opacity: 0.7; box-shadow: 0 0 0 5px transparent; }
}

.next-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.next-patch {
  width: 52px;
  height: 52px;
  object-fit: contain;
  flex-shrink: 0;
  opacity: 0.9;
  filter: drop-shadow(0 1px 4px rgba(0,0,0,0.3));
}

.next-patch-placeholder {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  color: var(--accent);
  opacity: 0.7;
}

.next-patch-placeholder svg {
  width: 100%;
  height: 100%;
}

.next-name {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text);
  text-transform: uppercase;
}

.next-meta {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 2px;
  display: flex;
  gap: 6px;
}

/* === RECOMMENDED ACTIONS === */
.highlights-section {
  background: var(--bg-surface);
  border-radius: var(--radius);
  padding: 20px;
}

.highlights-ai {
  border-left: 3px solid transparent;
  border-image: linear-gradient(180deg, var(--accent), var(--accent-blue)) 1;
}

.highlights-header {
  margin-bottom: 14px;
}

.highlights-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.highlights-title-row .section-label {
  margin-bottom: 0;
}

.highlights-ai-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 10px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 15%, transparent), color-mix(in srgb, var(--accent-blue) 15%, transparent));
  color: var(--accent);
}

.sparkle-icon {
  flex-shrink: 0;
}

.highlights-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 8px;
}

.highlight-card {
  border-left: 2px solid var(--border-strong);
  transition: border-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.highlights-ai .highlight-card {
  border-left-color: color-mix(in srgb, var(--accent) 40%, var(--border-strong));
}

/* Action card top row: icon + label + priority */
.hc-top {
  display: flex;
  align-items: center;
  gap: 6px;
}

.hc-action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  flex-shrink: 0;
}

.hc-action-icon.icon-optimize { color: var(--accent); background: var(--accent-dim); }
.hc-action-icon.icon-investigate { color: var(--accent-blue); background: color-mix(in srgb, var(--accent-blue) 12%, transparent); }
.hc-action-icon.icon-scale { color: var(--success); background: color-mix(in srgb, var(--success) 12%, transparent); }
.hc-action-icon.icon-reduce { color: var(--accent-cyan); background: color-mix(in srgb, var(--accent-cyan) 12%, transparent); }
.hc-action-icon.icon-monitor { color: var(--text-muted); background: var(--chart-track); }

.hc-action-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}

.hc-priority {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 1px 6px;
  border-radius: 3px;
  line-height: 1.4;
}

.priority-high { color: var(--error); background: color-mix(in srgb, var(--error) 14%, transparent); }
.priority-medium { color: var(--warning); background: color-mix(in srgb, var(--warning) 14%, transparent); }
.priority-low { color: var(--text-muted); background: var(--chart-track); }

.highlight-text {
  font-size: 0.86rem;
  color: var(--text-secondary);
  line-height: 1.55;
}

/* Domain pills */
.hc-domains {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: auto;
}

.hc-domain-pill {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 1px 6px;
  border-radius: 3px;
  background: var(--bg-hover);
  color: var(--text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .bento-hero {
    min-height: 220px;
  }
  .bento-stats {
    grid-template-columns: repeat(3, 1fr);
  }
  .stat-value { font-size: 1.4rem; }
  .stat-name { font-size: 0.7rem; }
  .bottom-grid {
    grid-template-columns: 1fr;
  }
  .hero-name { font-size: 1.6rem; }
  .hero-patch { width: 72px; height: 72px; }
  .hero-row { gap: 16px; }
  .hero-meta { flex-wrap: wrap; font-size: 0.82rem; }
  .hero-details { max-width: 100%; }
  .highlights-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .bento-hero { min-height: 180px; }
  .bento-stats { grid-template-columns: 1fr; }
  .hero-name { font-size: 1.3rem; }
  .hero-patch { width: 56px; height: 56px; }
  .hero-meta { font-size: 0.75rem; gap: 5px; }
  .stat-value { font-size: 1.2rem; }
  .stat-name { font-size: 0.62rem; }
  .stacked-legend-item { font-size: 0.65rem; }
}
</style>
