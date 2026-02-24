<template>
  <div>
    <div class="detail-back">
      <router-link
        to="/launches"
        class="back-link"
      >
        &larr; All Launches
      </router-link>
    </div>

    <div
      v-if="loading"
      class="detail-loading"
    >
      <SkeletonLoader
        variant="hero"
        height="320px"
      />
      <SkeletonLoader
        variant="text"
        :count="4"
      />
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
    </div>

    <ErrorState
      v-else-if="error"
      :message="error"
      @retry="load"
    />

    <template v-else-if="data">
      <!-- HERO -->
      <div
        class="detail-hero surface"
        :class="{ 'no-image': !heroImage }"
      >
        <div
          v-if="heroImage"
          class="hero-bg"
          :style="{ backgroundImage: `url(${heroImage})` }"
        />
        <div class="hero-overlay">
          <img
            v-if="data.links?.patch_large || data.links?.patch_small"
            :src="data.links.patch_large || data.links.patch_small"
            class="detail-patch"
            alt="Mission patch"
            width="120"
            height="120"
          >
          <div class="hero-info">
            <span class="flight-number">#{{ data.flight_number }}</span>
            <h1 class="detail-name">
              {{ data.name }}
            </h1>
            <div class="hero-meta">
              <span v-if="data.rocket_name">{{ data.rocket_name }}</span>
              <span
                v-if="data.rocket_name"
                class="sep"
              >·</span>
              <span v-if="data.launchpad_name">{{ data.launchpad_name }}</span>
              <span
                v-if="data.launchpad_name"
                class="sep"
              >·</span>
              <span>{{ formatDate(data.date_utc) }}</span>
            </div>
            <span
              class="status-badge"
              :class="statusClass"
            >{{ statusLabel }}</span>
          </div>
        </div>
      </div>

      <!-- DETAILS TEXT -->
      <div
        v-if="data.details"
        class="surface detail-section"
      >
        <span class="section-label">Mission Details</span>
        <p class="detail-text">
          {{ data.details }}
        </p>
      </div>

      <!-- GRID: Cores + Payloads -->
      <div class="detail-grid section-gap">
        <!-- CORES -->
        <div
          v-if="data.cores.length"
          class="surface detail-section"
        >
          <span class="section-label">Boosters</span>
          <div class="card-list">
            <div
              v-for="(core, i) in data.cores"
              :key="i"
              class="info-card"
            >
              <div class="card-row">
                <span class="card-label">Booster</span>
                <span class="card-value mono">{{ core.serial || '—' }} <span
                  v-if="core.flight"
                  class="text-muted"
                >(flight #{{ core.flight }})</span></span>
              </div>
              <div class="card-row">
                <span class="card-label">Reused</span>
                <span
                  class="card-value"
                  :class="core.reused ? 'text-accent' : ''"
                >{{ core.reused ? 'Yes' : 'No' }}</span>
              </div>
              <div
                v-if="core.landing_attempt !== null"
                class="card-row"
              >
                <span class="card-label">Landing</span>
                <span
                  class="card-value"
                  :class="core.landing_success ? 'text-success' : 'text-error'"
                >
                  {{ core.landing_success ? 'Success' : core.landing_attempt ? 'Failed' : 'No attempt' }}
                  <span
                    v-if="core.landing_type"
                    class="landing-type"
                  >{{ core.landing_type }}
                    <InfoTip v-if="core.landing_type === 'RTLS'">Return to Launch Site — booster flies back to land at the launch pad.</InfoTip>
                    <InfoTip v-else-if="core.landing_type === 'ASDS'">Autonomous Spaceport Drone Ship — booster lands on a floating ocean platform.</InfoTip>
                    <InfoTip v-else-if="core.landing_type === 'Ocean'">Controlled descent into the ocean (no recovery attempted).</InfoTip>
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- PAYLOADS -->
        <div
          v-if="data.payloads.length"
          class="surface detail-section"
        >
          <span class="section-label">Payloads</span>
          <div class="card-list">
            <div
              v-for="payload in data.payloads"
              :key="payload.id"
              class="info-card"
            >
              <div class="card-row">
                <span class="card-label">Name</span>
                <span class="card-value">{{ payload.name }}</span>
              </div>
              <div
                v-if="payload.type"
                class="card-row"
              >
                <span class="card-label">Type</span>
                <span class="card-value">{{ payload.type }}</span>
              </div>
              <div
                v-if="payload.customers.length"
                class="card-row"
              >
                <span class="card-label">Customer</span>
                <span class="card-value">{{ payload.customers.join(', ') }}</span>
              </div>
              <div
                v-if="payload.mass_kg"
                class="card-row"
              >
                <span class="card-label">Mass</span>
                <span class="card-value mono">{{ payload.mass_kg.toLocaleString() }} kg</span>
              </div>
              <div
                v-if="payload.orbit"
                class="card-row"
              >
                <span class="card-label">
                  Orbit
                  <InfoTip>The target orbit for this payload. Common types: LEO (Low Earth, 200–2,000 km), GTO (transfer to geostationary), SSO (sun-synchronous).</InfoTip>
                </span>
                <span class="card-value">{{ payload.orbit }}</span>
              </div>
              <div
                v-if="payload.regime"
                class="card-row"
              >
                <span class="card-label">
                  Regime
                  <InfoTip>The orbital regime describes the altitude band and characteristics of the orbit.</InfoTip>
                </span>
                <span class="card-value">{{ payload.regime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CREW -->
      <div
        v-if="data.crew.length"
        class="surface detail-section section-gap"
      >
        <span class="section-label">Crew</span>
        <div class="crew-grid">
          <div
            v-for="member in data.crew"
            :key="member.id"
            class="crew-card"
          >
            <img
              v-if="member.image"
              :src="member.image"
              class="crew-image"
              :alt="member.name"
              width="80"
              height="80"
            >
            <div class="crew-info">
              <span class="crew-name">{{ member.name }}</span>
              <span
                v-if="member.agency"
                class="crew-agency"
              >{{ member.agency }}</span>
              <span
                v-if="member.role"
                class="crew-role"
              >{{ member.role }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- FAILURES -->
      <div
        v-if="data.failures.length"
        class="surface detail-section section-gap"
      >
        <span class="section-label failure-label">Failure Details</span>
        <div
          v-for="(f, i) in data.failures"
          :key="i"
          class="failure-item"
        >
          <div
            v-if="f.time !== null"
            class="card-row"
          >
            <span class="card-label">
              Time
              <InfoTip>T+ means seconds after liftoff.</InfoTip>
            </span>
            <span class="card-value mono">T+{{ f.time }}s</span>
          </div>
          <div
            v-if="f.altitude !== null"
            class="card-row"
          >
            <span class="card-label">Altitude</span>
            <span class="card-value mono">{{ f.altitude }} km</span>
          </div>
          <div
            v-if="f.reason"
            class="card-row"
          >
            <span class="card-label">Reason</span>
            <span class="card-value">{{ f.reason }}</span>
          </div>
        </div>
      </div>

      <!-- FAIRINGS -->
      <div
        v-if="data.fairings_recovered !== null || data.static_fire_date_utc"
        class="surface detail-section detail-mini-grid"
      >
        <div
          v-if="data.fairings_recovered !== null"
          class="mini-item"
        >
          <span class="card-label">
            Fairings Recovered
            <InfoTip>Fairings are the nose cone halves that protect the payload during launch. SpaceX tries to recover and reuse them.</InfoTip>
          </span>
          <span
            class="card-value"
            :class="data.fairings_recovered ? 'text-success' : 'text-error'"
          >{{ data.fairings_recovered ? 'Yes' : 'No' }}</span>
        </div>
        <div
          v-if="data.fairings_reused !== null"
          class="mini-item"
        >
          <span class="card-label">Fairings Reused</span>
          <span class="card-value">{{ data.fairings_reused ? 'Yes' : 'No' }}</span>
        </div>
        <div
          v-if="data.static_fire_date_utc"
          class="mini-item"
        >
          <span class="card-label">Static Fire</span>
          <span class="card-value mono">{{ formatDate(data.static_fire_date_utc) }}</span>
        </div>
      </div>

      <!-- LINKS -->
      <div
        v-if="hasLinks"
        class="surface detail-section section-gap"
      >
        <span class="section-label">Links</span>
        <div class="links-row">
          <a
            v-if="data.links?.webcast"
            :href="data.links.webcast"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Webcast</a>
          <a
            v-if="data.links?.article"
            :href="data.links.article"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Article</a>
          <a
            v-if="data.links?.wikipedia"
            :href="data.links.wikipedia"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Wikipedia</a>
          <a
            v-if="data.links?.presskit"
            :href="data.links.presskit"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Press Kit</a>
          <a
            v-if="data.links?.reddit_campaign"
            :href="data.links.reddit_campaign"
            target="_blank"
            rel="noopener"
            class="link-btn"
          >Reddit</a>
        </div>
      </div>

      <!-- FLICKR GALLERY -->
      <div
        v-if="data.links?.flickr_original?.length"
        class="surface detail-section section-gap"
      >
        <span class="section-label">Gallery</span>
        <div class="gallery-grid">
          <img
            v-for="(img, i) in data.links.flickr_original"
            :key="i"
            :src="img"
            class="gallery-img"
            alt="Mission photo"
            width="400"
            height="267"
            loading="lazy"
            @click="openLightbox(i)"
          >
        </div>
      </div>

      <ImageLightbox
        v-if="data.links?.flickr_original?.length"
        v-model:visible="lightboxOpen"
        :images="data.links.flickr_original"
        :start-index="lightboxIndex"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchLaunchDetail } from '@/api'
import { formatDate } from '@/utils/formatDate'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import ImageLightbox from '@/components/common/ImageLightbox.vue'
import InfoTip from '@/components/common/InfoTip.vue'
import type { LaunchDetail } from '@/types'

const route = useRoute()
const data = ref<LaunchDetail | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)

function openLightbox(index: number): void {
  lightboxIndex.value = index
  lightboxOpen.value = true
}

const heroImage = computed((): string | null => {
  const imgs = data.value?.links?.flickr_original || []
  return imgs.length > 0 ? imgs[0] : null
})

const statusClass = computed((): string => {
  if (data.value?.upcoming) return 'status-upcoming'
  return data.value?.success ? 'status-success' : 'status-fail'
})

const statusLabel = computed((): string => {
  if (data.value?.upcoming) return 'UPCOMING'
  return data.value?.success ? 'SUCCESS' : 'FAILED'
})

const hasLinks = computed((): boolean => {
  const l = data.value?.links
  return !!l && !!(l.webcast || l.article || l.wikipedia || l.presskit || l.reddit_campaign)
})

async function load(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchLaunchDetail(route.params.id as string)
  } catch {
    error.value = 'Failed to load launch details.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.detail-back {
  margin-bottom: 16px;
}

.back-link {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.back-link:hover {
  color: var(--accent);
}

.detail-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-error {
  text-align: center;
  padding: 40px;
}

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
.detail-hero {
  position: relative;
  min-height: 280px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: flex-end;
}

.detail-hero.no-image {
  background: linear-gradient(135deg, #0c0c1d 0%, #1a1a2e 40%, #16213e 70%, #0f3460 100%);
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: brightness(0.45);
}

.hero-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.35) 50%, rgba(0,0,0,0.2) 100%);
}

.hero-overlay {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 32px;
  width: 100%;
}

.detail-patch {
  width: 120px;
  height: 120px;
  object-fit: contain;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 16px rgba(0,0,0,0.5));
}

.hero-info {
  flex: 1;
  min-width: 0;
}

.flight-number {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.detail-name {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  line-height: 1.1;
  margin-top: 4px;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
}

.sep { opacity: 0.4; }

.status-badge {
  display: inline-block;
  margin-top: 12px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 4px 12px;
  border-radius: 3px;
  font-weight: 600;
}

.status-success { color: var(--success); background: color-mix(in srgb, var(--success) 18%, transparent); }
.status-fail { color: var(--error); background: color-mix(in srgb, var(--error) 18%, transparent); }
.status-upcoming { color: var(--accent); background: color-mix(in srgb, var(--accent) 18%, transparent); }

/* SECTIONS */
.detail-section {
  margin-top: 2px;
  border-radius: var(--radius);
}

.detail-text {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.65;
  max-width: 720px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  margin-top: 2px;
}

/* INFO CARDS */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-card:last-child { border-bottom: none; padding-bottom: 0; }

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}

.card-value {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--text);
  font-weight: 500;
}

.card-value.mono { font-variant-numeric: tabular-nums; }
.text-accent { color: var(--accent); }
.text-success { color: var(--success); }
.text-error { color: var(--error); }

.landing-type {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-left: 6px;
}

/* CREW */
.crew-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.crew-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border-radius: var(--radius);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
}

.crew-image {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.crew-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.crew-name {
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.crew-agency {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.crew-role {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
}

/* FAILURES */
.failure-label { color: var(--error); }

.failure-item {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.failure-item:last-child { border-bottom: none; }

/* MINI GRID */
.detail-mini-grid {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.mini-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* LINKS */
.links-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

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

.link-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

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
  .detail-grid { grid-template-columns: 1fr; }
  .detail-name { font-size: 1.5rem; }
  .detail-patch { width: 80px; height: 80px; }
  .hero-overlay { padding: 20px; gap: 16px; }
  .crew-grid { grid-template-columns: 1fr; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
}

@media (max-width: 640px) {
  .detail-name { font-size: 1.2rem; }
  .detail-patch { width: 60px; height: 60px; }
  .hero-overlay { padding: 16px; flex-direction: column; align-items: flex-start; gap: 12px; }
  .gallery-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
}
</style>
