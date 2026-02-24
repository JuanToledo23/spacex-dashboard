<template>
  <div>
    <div class="detail-back">
      <router-link
        to="/fleet"
        class="back-link"
      >
        &larr; Fleet
      </router-link>
    </div>

    <div
      v-if="loading"
      class="detail-loading"
    >
      <SkeletonLoader
        variant="hero"
        height="300px"
      />
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 16px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <SkeletonLoader
        variant="text"
        :count="3"
      />
    </div>

    <ErrorState
      v-else-if="error"
      :message="error"
      @retry="load"
    />

    <template v-else-if="data">
      <!-- HERO -->
      <div class="rocket-hero surface">
        <div
          v-if="heroImage"
          class="hero-bg"
          :style="{ backgroundImage: `url(${heroImage})` }"
        />
        <div class="hero-overlay">
          <div class="hero-info">
            <span
              class="rocket-status"
              :class="data.active ? 'active' : 'retired'"
            >
              {{ data.active ? 'Active' : 'Retired' }}
            </span>
            <h1 class="rocket-name">
              {{ data.name }}
            </h1>
            <div class="hero-meta">
              <span v-if="data.country">{{ data.country }}</span>
              <span
                v-if="data.country && data.first_flight"
                class="sep"
              >·</span>
              <span v-if="data.first_flight">First flight {{ data.first_flight }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- STATS GRID -->
      <div class="stats-row">
        <div class="stat-card surface-dense">
          <span class="stat-val mono">{{ data.cost_per_launch ? '$' + (data.cost_per_launch / 1e6).toFixed(0) + 'M' : '—' }}</span>
          <span class="stat-lbl">Cost / Launch</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val mono accent">{{ data.success_rate_pct }}%</span>
          <span class="stat-lbl">Success Rate</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val mono">{{ data.launch_count }}</span>
          <span class="stat-lbl">Total Launches</span>
        </div>
        <div class="stat-card surface-dense">
          <span class="stat-val mono">{{ data.stages }}</span>
          <span class="stat-lbl">Stages</span>
        </div>
        <div
          v-if="data.boosters"
          class="stat-card surface-dense"
        >
          <span class="stat-val mono">{{ data.boosters }}</span>
          <span class="stat-lbl">Boosters</span>
        </div>
      </div>

      <SectionNav :sections="rocketSections" />

      <!-- DESCRIPTION -->
      <div
        v-if="data.description"
        id="rkt-overview"
        data-section-nav
        class="surface detail-section"
      >
        <span class="section-label">About</span>
        <p class="desc-text">
          {{ data.description }}
        </p>
      </div>

      <!-- DIMENSIONS -->
      <div
        id="rkt-dims"
        data-section-nav
        class="surface detail-section section-gap"
      >
        <span class="section-label">Dimensions</span>
        <div class="dims-grid">
          <div
            v-if="data.height_meters"
            class="dim-item"
          >
            <span class="dim-val mono">{{ data.height_meters }}m</span>
            <span class="dim-lbl">Height</span>
          </div>
          <div
            v-if="data.diameter_meters"
            class="dim-item"
          >
            <span class="dim-val mono">{{ data.diameter_meters }}m</span>
            <span class="dim-lbl">Diameter</span>
          </div>
          <div
            v-if="data.mass_kg"
            class="dim-item"
          >
            <span class="dim-val mono">{{ (data.mass_kg / 1000).toFixed(0) }}t</span>
            <span class="dim-lbl">Mass</span>
          </div>
          <div
            v-if="data.landing_legs_number"
            class="dim-item"
          >
            <span class="dim-val mono">{{ data.landing_legs_number }}</span>
            <span class="dim-lbl">Landing Legs</span>
          </div>
          <div
            v-if="data.landing_legs_material"
            class="dim-item"
          >
            <span class="dim-val">{{ data.landing_legs_material }}</span>
            <span class="dim-lbl">Leg Material</span>
          </div>
        </div>
      </div>

      <!-- ENGINES -->
      <div
        v-if="data.engines"
        id="rkt-engines"
        data-section-nav
        class="surface detail-section section-gap"
      >
        <span class="section-label">Engines</span>
        <div class="engine-grid">
          <div
            v-if="data.engines.number"
            class="eng-item"
          >
            <span class="eng-val mono">{{ data.engines.number }}</span>
            <span class="eng-lbl">Count</span>
          </div>
          <div
            v-if="data.engines.type"
            class="eng-item"
          >
            <span class="eng-val">{{ data.engines.type }} {{ data.engines.version || '' }}</span>
            <span class="eng-lbl">Type</span>
          </div>
          <div
            v-if="data.engines.thrust_sea_level_kn"
            class="eng-item"
          >
            <span class="eng-val mono">{{ data.engines.thrust_sea_level_kn }} kN</span>
            <span class="eng-lbl">
              Thrust (Sea Level)
              <InfoTip>Kilonewtons — unit of force. 1 kN ≈ the weight of 100 kg on Earth.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.thrust_vacuum_kn"
            class="eng-item"
          >
            <span class="eng-val mono">{{ data.engines.thrust_vacuum_kn }} kN</span>
            <span class="eng-lbl">
              Thrust (Vacuum)
              <InfoTip>Engine force measured in the vacuum of space, where there is no atmospheric drag.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.isp_sea_level"
            class="eng-item"
          >
            <span class="eng-val mono">{{ data.engines.isp_sea_level }}s</span>
            <span class="eng-lbl">
              ISP (Sea Level)
              <InfoTip>Specific Impulse — measures engine efficiency. More seconds = burns fuel more efficiently. Measured at sea level atmospheric pressure.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.isp_vacuum"
            class="eng-item"
          >
            <span class="eng-val mono">{{ data.engines.isp_vacuum }}s</span>
            <span class="eng-lbl">
              ISP (Vacuum)
              <InfoTip>Specific Impulse in vacuum — same efficiency metric but in space, where engines typically perform better.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.propellant_1"
            class="eng-item"
          >
            <span class="eng-val">{{ data.engines.propellant_1 }}</span>
            <span class="eng-lbl">
              Propellant 1
              <InfoTip>The fuel component. Rockets use two propellants that react together to produce thrust.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.propellant_2"
            class="eng-item"
          >
            <span class="eng-val">{{ data.engines.propellant_2 }}</span>
            <span class="eng-lbl">
              Propellant 2
              <InfoTip>The oxidizer component — provides the oxygen needed for combustion in the vacuum of space.</InfoTip>
            </span>
          </div>
          <div
            v-if="data.engines.thrust_to_weight"
            class="eng-item"
          >
            <span class="eng-val mono accent">{{ data.engines.thrust_to_weight }}</span>
            <span class="eng-lbl">
              Thrust-to-Weight
              <InfoTip>Ratio of engine thrust to its own weight. Must be &gt; 1 for the rocket to lift off the ground.</InfoTip>
            </span>
          </div>
        </div>
      </div>

      <!-- PAYLOAD CAPACITY -->
      <div
        v-if="data.payload_weights.length"
        id="rkt-payload"
        data-section-nav
        class="surface detail-section section-gap"
      >
        <span class="section-label">Payload Capacity</span>
        <div class="payload-bars">
          <div
            v-for="pw in data.payload_weights"
            :key="pw.id"
            class="pw-row"
          >
            <div class="pw-top">
              <span class="pw-name">{{ pw.name }}</span>
              <span class="pw-val mono">{{ pw.kg.toLocaleString() }} kg</span>
            </div>
            <div class="pw-bar-track">
              <div
                class="pw-bar-fill"
                :style="{ width: payloadBarWidth(pw.kg) }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- STAGES (side by side) -->
      <div
        v-if="data.first_stage || data.second_stage"
        id="rkt-stages"
        data-section-nav
        class="stages-grid section-gap"
      >
        <div
          v-if="data.first_stage"
          class="surface detail-section"
        >
          <span class="section-label">First Stage</span>
          <div class="stage-rows">
            <div
              v-if="data.first_stage.engines"
              class="card-row"
            >
              <span class="card-label">Engines</span>
              <span class="card-value mono">{{ data.first_stage.engines }}</span>
            </div>
            <div
              v-if="data.first_stage.thrust_sea_level_kn"
              class="card-row"
            >
              <span class="card-label">Thrust (Sea Level)</span>
              <span class="card-value mono">{{ data.first_stage.thrust_sea_level_kn }} kN</span>
            </div>
            <div
              v-if="data.first_stage.thrust_vacuum_kn"
              class="card-row"
            >
              <span class="card-label">Thrust (Vacuum)</span>
              <span class="card-value mono">{{ data.first_stage.thrust_vacuum_kn }} kN</span>
            </div>
            <div
              v-if="data.first_stage.fuel_amount_tons"
              class="card-row"
            >
              <span class="card-label">Fuel</span>
              <span class="card-value mono">{{ data.first_stage.fuel_amount_tons }} tonnes</span>
            </div>
            <div
              v-if="data.first_stage.burn_time_sec"
              class="card-row"
            >
              <span class="card-label">Burn Time</span>
              <span class="card-value mono">{{ data.first_stage.burn_time_sec }} sec</span>
            </div>
            <div class="card-row">
              <span class="card-label">Reusable</span>
              <span
                class="card-value"
                :class="data.first_stage.reusable ? 'text-success' : 'text-muted'"
              >{{ data.first_stage.reusable ? 'Yes' : 'No' }}</span>
            </div>
          </div>
        </div>
        <div
          v-if="data.second_stage"
          class="surface detail-section"
        >
          <span class="section-label">Second Stage</span>
          <div class="stage-rows">
            <div
              v-if="data.second_stage.engines"
              class="card-row"
            >
              <span class="card-label">Engines</span>
              <span class="card-value mono">{{ data.second_stage.engines }}</span>
            </div>
            <div
              v-if="data.second_stage.thrust_sea_level_kn"
              class="card-row"
            >
              <span class="card-label">Thrust (Sea Level)</span>
              <span class="card-value mono">{{ data.second_stage.thrust_sea_level_kn }} kN</span>
            </div>
            <div
              v-if="data.second_stage.thrust_vacuum_kn"
              class="card-row"
            >
              <span class="card-label">Thrust (Vacuum)</span>
              <span class="card-value mono">{{ data.second_stage.thrust_vacuum_kn }} kN</span>
            </div>
            <div
              v-if="data.second_stage.fuel_amount_tons"
              class="card-row"
            >
              <span class="card-label">Fuel</span>
              <span class="card-value mono">{{ data.second_stage.fuel_amount_tons }} tonnes</span>
            </div>
            <div
              v-if="data.second_stage.burn_time_sec"
              class="card-row"
            >
              <span class="card-label">Burn Time</span>
              <span class="card-value mono">{{ data.second_stage.burn_time_sec }} sec</span>
            </div>
            <div class="card-row">
              <span class="card-label">Reusable</span>
              <span
                class="card-value"
                :class="data.second_stage.reusable ? 'text-success' : 'text-muted'"
              >{{ data.second_stage.reusable ? 'Yes' : 'No' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- LINKS -->
      <div
        v-if="data.wikipedia"
        class="surface detail-section"
      >
        <div class="links-row">
          <a
            :href="data.wikipedia"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Wikipedia</a>
        </div>
      </div>

      <!-- GALLERY -->
      <div
        v-if="data.flickr_images.length > 1"
        class="surface detail-section"
      >
        <span class="section-label">Gallery</span>
        <div class="gallery-grid">
          <img
            v-for="(img, i) in data.flickr_images"
            :key="i"
            :src="img"
            class="gallery-img"
            alt="Rocket photo"
            width="400"
            height="267"
            loading="lazy"
            @click="openLightbox(i)"
          >
        </div>
      </div>

      <ImageLightbox
        v-if="data.flickr_images.length"
        v-model:visible="lightboxOpen"
        :images="data.flickr_images"
        :start-index="lightboxIndex"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchRocketDetail } from '@/api'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import ImageLightbox from '@/components/common/ImageLightbox.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import SectionNav from '@/components/common/SectionNav.vue'
import type { RocketDetail } from '@/types'

const rocketSections = [
  { id: 'rkt-overview', label: 'Overview' },
  { id: 'rkt-dims', label: 'Dimensions' },
  { id: 'rkt-engines', label: 'Engines' },
  { id: 'rkt-payload', label: 'Payload' },
  { id: 'rkt-stages', label: 'Stages' },
]

const route = useRoute()
const data = ref<RocketDetail | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)

function openLightbox(index: number): void {
  lightboxIndex.value = index
  lightboxOpen.value = true
}

const heroImage = computed((): string | null => {
  const imgs = data.value?.flickr_images || []
  return imgs.length > 0 ? imgs[0] : null
})

function payloadBarWidth(kg: number): string {
  if (!data.value?.payload_weights?.length) return '0%'
  const max = Math.max(...data.value.payload_weights.map((p) => p.kg))
  return Math.round((kg / max) * 100) + '%'
}

async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchRocketDetail(route.params.id as string)
  } catch {
    error.value = 'Failed to load rocket details.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.detail-back { margin-bottom: 16px; }

.back-link {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.15s;
}
.back-link:hover { color: var(--accent); }

.detail-loading { display: flex; flex-direction: column; gap: 12px; }

.detail-error { text-align: center; padding: 40px; }

.btn-retry {
  margin-top: 12px;
  padding: 8px 20px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  background: var(--accent);
  color: var(--bg);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
}

/* HERO */
.rocket-hero {
  position: relative;
  min-height: 300px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: flex-end;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: brightness(0.4);
}

.hero-overlay {
  position: relative;
  z-index: 1;
  padding: 36px;
  width: 100%;
}

.hero-info { min-width: 0; }

.rocket-status {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 3px 10px;
  border-radius: 3px;
  font-weight: 600;
}

.rocket-status.active { color: var(--success); background: color-mix(in srgb, var(--success) 18%, transparent); }
.rocket-status.retired { color: var(--text-muted); background: var(--chart-track); }

.rocket-name {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  line-height: 1.1;
  margin-top: 10px;
}

.hero-meta {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
}

.sep { opacity: 0.4; }

/* STATS ROW */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 2px;
  margin-top: 2px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 16px 8px;
  gap: 4px;
}

.stat-val {
  font-family: var(--font-mono);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}

.stat-val.accent { color: var(--accent); }

.stat-lbl {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* SECTIONS */
.detail-section {
  margin-top: 2px;
  border-radius: var(--radius);
}

.desc-text {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.65;
  max-width: 720px;
}

/* DIMENSIONS */
.dims-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 20px;
}

.dim-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }

.dim-val {
  font-family: var(--font-mono);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
}

.dim-lbl {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

/* ENGINES */
.engine-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.eng-item { display: flex; flex-direction: column; gap: 3px; }

.eng-val {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text);
}

.eng-val.accent { color: var(--accent); }

.eng-lbl {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

/* PAYLOAD CAPACITY */
.payload-bars { display: flex; flex-direction: column; gap: 12px; }

.pw-row { display: flex; flex-direction: column; gap: 4px; }

.pw-top { display: flex; justify-content: space-between; align-items: center; }

.pw-name {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.pw-val {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text);
}

.pw-bar-track {
  height: 10px;
  background: var(--chart-track);
  border-radius: 2px;
  overflow: hidden;
}

.pw-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--accent);
  opacity: 0.7;
  transition: width 0.5s ease;
}

/* STAGES */
.stages-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  margin-top: 2px;
}

.stage-rows { display: flex; flex-direction: column; gap: 8px; }

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid var(--border);
}

.card-row:last-child { border-bottom: none; }

.card-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.card-value {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text);
  font-weight: 500;
}

.mono { font-variant-numeric: tabular-nums; }
.text-success { color: var(--success); }
.text-muted { color: var(--text-muted); }

/* LINKS */
.links-row { display: flex; gap: 10px; flex-wrap: wrap; }

.link-btn {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 6px 16px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s;
}
.link-btn:hover { color: var(--accent); border-color: var(--accent); }

/* GALLERY */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
}

.gallery-img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  border-radius: var(--radius);
  cursor: pointer;
  transition: opacity 0.15s;
}

.gallery-img:hover {
  opacity: 0.85;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .stages-grid { grid-template-columns: 1fr; }
  .rocket-name { font-size: 1.8rem; }
  .hero-overlay { padding: 24px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
}

@media (max-width: 640px) {
  .rocket-name { font-size: 1.4rem; }
  .hero-overlay { padding: 16px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
}
</style>
