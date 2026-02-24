<template>
  <section class="starman-page">
    <div
      v-if="loading"
      class="loading-state"
    >
      <SkeletonLoader
        variant="hero"
        height="320px"
      />
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 24px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <SkeletonLoader
        variant="chart"
        height="260px"
      />
    </div>

    <template v-else-if="data">
      <!-- Hero -->
      <div
        class="starman-hero"
        :style="heroStyle"
      >
        <div class="hero-overlay" />
        <div class="hero-content">
          <span class="hero-tag">DEEP SPACE</span>
          <h1 class="hero-title">
            Starman
          </h1>
          <p class="hero-sub">
            {{ data.name }} &mdash; Launched {{ formatDate(data.launch_date_utc) }}
          </p>
          <p class="hero-context">
            A Tesla Roadster with a mannequin in a spacesuit, launched on the first Falcon Heavy test flight. It has been orbiting the Sun ever since.
          </p>
        </div>
      </div>

      <!-- Hero Stat: Speed -->
      <div class="speed-hero surface">
        <span class="stat-label">Current Speed</span>
        <span class="speed-value accent">{{ formatNum(data.speed_kph) }} <small>km/h</small></span>
        <span class="human-context">~{{ Math.round(data.speed_kph / 3600).toLocaleString() }}&times; faster than a bullet — fast enough to circle Earth in ~30 minutes</span>
      </div>

      <!-- Secondary Stats -->
      <div class="stats-grid">
        <div class="stat-card surface">
          <span
            class="stat-icon"
            aria-hidden="true"
          >⊕</span>
          <span class="stat-label">Earth Distance</span>
          <span class="stat-value">{{ formatDist(data.earth_distance_km) }}</span>
          <span class="stat-unit">million km</span>
          <span class="human-context">~{{ Math.round(data.earth_distance_km / 384400) }}&times; the Earth–Moon distance</span>
        </div>
        <div class="stat-card surface">
          <span
            class="stat-icon"
            aria-hidden="true"
          >♂</span>
          <span class="stat-label">Mars Distance</span>
          <span class="stat-value">{{ formatDist(data.mars_distance_km) }}</span>
          <span class="stat-unit">million km</span>
          <span class="human-context">~{{ Math.round(data.mars_distance_km / 384400) }}&times; the Earth–Moon distance</span>
        </div>
        <div class="stat-card surface">
          <span
            class="stat-icon"
            aria-hidden="true"
          >⟳</span>
          <span class="stat-label">Orbit Period</span>
          <span class="stat-value">{{ Math.round(data.period_days) }}</span>
          <span class="stat-unit">days</span>
          <span class="human-context">~{{ (data.period_days / 365.25).toFixed(1) }} years per orbit around the Sun</span>
        </div>
      </div>

      <!-- Orbit Visualization -->
      <div class="section-block surface">
        <h2 class="section-title">
          Heliocentric Orbit
          <InfoTip>An orbit around the Sun (not the Earth). Starman travels between Earth's and Mars' orbits.</InfoTip>
        </h2>
        <RoadsterOrbitChart
          :apoapsis="data.apoapsis_au"
          :periapsis="data.periapsis_au"
          :semi-major-axis="data.semi_major_axis_au || 1.325"
        />
      </div>

      <!-- Orbital Parameters (collapsible) -->
      <div class="section-block surface">
        <h2 class="section-title">
          Orbital Parameters
        </h2>
        <div class="params-grid">
          <div class="param-item">
            <span class="param-label">
              Orbit Type
              <InfoTip>The type of orbit: heliocentric means it orbits the Sun, not the Earth.</InfoTip>
            </span>
            <span class="param-value">{{ data.orbit_type }}</span>
          </div>
          <div class="param-item">
            <span class="param-label">
              Apoapsis
              <InfoTip>The farthest point of the orbit from the Sun.</InfoTip>
            </span>
            <span class="param-value">{{ data.apoapsis_au.toFixed(4) }} AU <small class="text-muted">(≈{{ Math.round(data.apoapsis_au * 149.6) }}M km)</small></span>
          </div>
          <div class="param-item">
            <span class="param-label">
              Periapsis
              <InfoTip>The closest point of the orbit to the Sun.</InfoTip>
            </span>
            <span class="param-value">{{ data.periapsis_au.toFixed(4) }} AU <small class="text-muted">(≈{{ Math.round(data.periapsis_au * 149.6) }}M km)</small></span>
          </div>
        </div>

        <Transition name="params-expand">
          <div
            v-if="showAllParams"
            class="params-grid params-extra"
          >
            <div
              v-if="data.semi_major_axis_au"
              class="param-item"
            >
              <span class="param-label">
                Semi-Major Axis
                <InfoTip>Half the longest diameter of the elliptical orbit — essentially the "average radius."</InfoTip>
              </span>
              <span class="param-value">{{ data.semi_major_axis_au.toFixed(4) }} AU <small class="text-muted">(≈{{ Math.round(data.semi_major_axis_au * 149.6) }}M km)</small></span>
            </div>
            <div
              v-if="data.eccentricity"
              class="param-item"
            >
              <span class="param-label">
                Eccentricity
                <InfoTip>How "oval" the orbit is. 0 = perfect circle, closer to 1 = very elongated.</InfoTip>
              </span>
              <span class="param-value">{{ data.eccentricity.toFixed(6) }}</span>
            </div>
            <div
              v-if="data.inclination"
              class="param-item"
            >
              <span class="param-label">
                Inclination
                <InfoTip>The tilt angle of the orbit relative to the plane of the solar system.</InfoTip>
              </span>
              <span class="param-value">{{ data.inclination.toFixed(4) }}°</span>
            </div>
          </div>
        </Transition>

        <button
          class="params-toggle"
          :aria-expanded="showAllParams ? 'true' : 'false'"
          aria-label="Toggle orbital parameters"
          @click="showAllParams = !showAllParams"
        >
          {{ showAllParams ? 'Show less' : 'Show all parameters' }}
          <span class="toggle-arrow">{{ showAllParams ? '▲' : '▼' }}</span>
        </button>
      </div>

      <!-- About Section -->
      <div
        v-if="data.details"
        class="section-block surface"
      >
        <h2 class="section-title">
          About the Roadster
        </h2>
        <p class="about-text">
          {{ data.details }}
        </p>
      </div>

      <!-- Links & Gallery -->
      <div class="links-row">
        <a
          v-if="data.wikipedia"
          :href="data.wikipedia"
          target="_blank"
          rel="noopener"
          class="ext-link surface"
        >
          Wikipedia &rarr;
        </a>
        <a
          v-if="data.video"
          :href="data.video"
          target="_blank"
          rel="noopener"
          class="ext-link surface"
        >
          Watch Launch &rarr;
        </a>
      </div>

      <div
        v-if="data.flickr_images && data.flickr_images.length"
        class="gallery"
      >
        <h2 class="section-title">
          Gallery
        </h2>
        <div class="gallery-grid">
          <img
            v-for="(img, i) in data.flickr_images"
            :key="i"
            :src="img"
            :alt="`Starman photo ${i + 1}`"
            class="gallery-img"
            width="400"
            height="267"
            loading="lazy"
            @click="openLightbox(i)"
          >
        </div>
      </div>

      <ImageLightbox
        v-if="data.flickr_images && data.flickr_images.length"
        v-model:visible="lightboxOpen"
        :images="data.flickr_images"
        :start-index="lightboxIndex"
      />
    </template>

    <ErrorState
      v-else
      message="Unable to load Starman data."
      @retry="loadData"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fetchRoadster } from '@/api'
import { formatDate } from '@/utils/formatDate'
import RoadsterOrbitChart from '@/components/charts/RoadsterOrbitChart.vue'
import ImageLightbox from '@/components/common/ImageLightbox.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import type { RoadsterData } from '@/types'

const data = ref<RoadsterData | null>(null)
const loading = ref(true)
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)
const showAllParams = ref(false)

function openLightbox(index: number): void {
  lightboxIndex.value = index
  lightboxOpen.value = true
}

async function loadData(): Promise<void> {
  loading.value = true
  data.value = null
  try {
    data.value = await fetchRoadster()
  } catch (e) {
    console.error('Failed to fetch roadster data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

const heroStyle = computed((): Record<string, string> => {
  if (data.value?.flickr_images?.length) {
    return { backgroundImage: `url(${data.value.flickr_images[0]})` }
  }
  return {}
})

function formatNum(n: number | null | undefined): string {
  if (!n) return '0'
  return Math.round(n).toLocaleString()
}

function formatDist(km: number | null | undefined): string {
  if (!km) return '0'
  return (km / 1_000_000).toFixed(2)
}
</script>

<style scoped>
.starman-page {
  max-width: 1080px;
  margin: 0 auto;
}

/* Hero */
.starman-hero {
  position: relative;
  width: 100%;
  min-height: 340px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-color: var(--bg-surface);
  margin-bottom: 32px;
  display: flex;
  align-items: flex-end;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.3) 50%, rgba(0, 0, 0, 0.1) 100%);
}

.hero-content {
  position: relative;
  padding: 32px;
  z-index: 1;
}

.hero-tag {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--accent);
  letter-spacing: 0.14em;
  display: block;
  margin-bottom: 8px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 3rem;
  font-weight: 700;
  color: #fafafa;
  margin: 0 0 6px;
}

.hero-sub {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.75);
  margin: 0;
}

.hero-context {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.55);
  margin-top: 8px;
  max-width: 520px;
  line-height: 1.5;
}

/* Stats */
.speed-hero {
  text-align: center;
  padding: 24px 20px;
  margin: 0 24px 16px;
}

.speed-value {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  line-height: 1.2;
  display: block;
  margin-top: 4px;
}

.speed-value small {
  font-size: 0.5em;
  opacity: 0.7;
}

.params-extra {
  margin-top: 12px;
}

.params-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px;
  margin-top: 12px;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all var(--transition);
}

.params-toggle:hover {
  color: var(--text);
  border-color: var(--border-strong);
}

.toggle-arrow {
  font-size: 0.65rem;
}

.params-expand-enter-active,
.params-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.params-expand-enter-from,
.params-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.params-expand-enter-to,
.params-expand-leave-from {
  opacity: 1;
  max-height: 300px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 0 24px 28px;
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-icon {
  font-size: 1.3rem;
  color: var(--accent);
  margin-bottom: 4px;
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.stat-unit {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* Sections */
.section-block {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin: 0 24px 28px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 16px;
}

/* Params Grid */
.params-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.param-value {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
}

/* About */
.about-text {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Links */
.links-row {
  display: flex;
  gap: 12px;
  margin: 0 24px 28px;
}

.ext-link {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 20px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
  transition: border-color 0.15s, background 0.15s;
}

.ext-link:hover {
  border-color: var(--accent);
  background: var(--accent-dim);
}

/* Gallery */
.gallery {
  margin: 0 24px 28px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.gallery-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: opacity 0.15s;
}

.gallery-img:hover {
  opacity: 0.85;
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
  .stats-grid { grid-template-columns: repeat(3, 1fr); margin: 0 16px 20px; }
  .speed-hero { margin: 0 16px 16px; }
  .params-grid { grid-template-columns: repeat(2, 1fr); }
  .starman-hero { min-height: 240px; }
  .hero-title { font-size: 2.2rem; }
  .section-block { margin: 0 16px 20px; }
  .links-row { margin: 0 16px 20px; flex-wrap: wrap; }
  .gallery { margin: 0 16px 20px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
}

@media (max-width: 640px) {
  .hero-title { font-size: 1.6rem; }
  .stats-grid { grid-template-columns: 1fr; margin: 0 12px 16px; gap: 10px; }
  .speed-hero { margin: 0 12px 12px; }
  .speed-value { font-size: 1.8rem; }
  .stat-value { font-size: 1.4rem; }
  .section-block { margin: 0 12px 16px; }
  .links-row { margin: 0 12px 16px; }
  .gallery { margin: 0 12px 16px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
  .params-grid { grid-template-columns: 1fr; }
}
</style>
