<template>
  <div>
    <ErrorState
      v-if="store.error"
      :message="store.error"
      @retry="store.load()"
    />

    <template v-else-if="store.loading">
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px">
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
        <SkeletonLoader variant="stat" />
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px">
        <SkeletonLoader
          variant="card"
          :count="4"
        />
      </div>
    </template>

    <template v-else-if="store.stats">
      <!-- View header -->
      <div class="view-header">
        <h1 class="view-header-title">
          Vehicle Fleet
        </h1>
        <p class="view-header-sub">
          SpaceX's active and retired launch vehicles, booster recovery statistics, and reuse milestones.
        </p>
      </div>

      <!-- Rocket Showcase — horizontal grid -->
      <div class="rocket-showcase">
        <div
          v-for="rocket in store.rockets"
          :key="rocket.id"
          class="rocket-card image-hero"
          :class="{ expanded: expandedRocket === rocket.id }"
          @click="toggleRocket(rocket.id)"
        >
          <div
            v-if="rocket.flickr_images?.length"
            class="image-hero-bg"
            :style="{ backgroundImage: `url(${rocket.flickr_images[0]})` }"
          />
          <div class="image-hero-content rocket-card-content">
            <span :class="['rocket-status', rocket.active ? 'active' : 'retired']">
              {{ rocket.active ? 'ACTIVE' : 'RETIRED' }}
            </span>
            <h2 class="rocket-name">
              {{ rocket.name }}
            </h2>
            <div class="rocket-stats-grid">
              <div class="rocket-stat-cell">
                <span class="rocket-stat-val">{{ rocket.launch_count }}</span>
                <span class="rocket-stat-lbl">Missions</span>
              </div>
              <div class="rocket-stat-cell">
                <span class="rocket-stat-val">{{ rocket.success_rate_pct }}%</span>
                <span class="rocket-stat-lbl">Success</span>
              </div>
              <div
                v-if="rocket.cost_per_launch"
                class="rocket-stat-cell"
              >
                <span class="rocket-stat-val">${{ (rocket.cost_per_launch / 1e6).toFixed(0) }}M</span>
                <span class="rocket-stat-lbl">Per Launch</span>
              </div>
              <div
                v-if="rocket.first_flight"
                class="rocket-stat-cell"
              >
                <span class="rocket-stat-val">{{ rocket.first_flight }}</span>
                <span class="rocket-stat-lbl">First Flight</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Expanded rocket details (below grid) -->
      <Transition name="expand-fade">
        <div
          v-if="expandedRocket && store.rockets.find(r => r.id === expandedRocket)"
          class="rocket-expanded surface"
        >
          <p class="rocket-desc">
            {{ store.rockets.find(r => r.id === expandedRocket)?.description }}
          </p>
          <button
            class="rocket-detail-btn"
            aria-label="View rocket full details"
            @click.stop="goToRocket(expandedRocket)"
          >
            View full details &rarr;
          </button>
        </div>
      </Transition>

      <!-- Booster Recovery Section -->
      <div class="recovery-grid section-gap">
        <div class="surface recovery-main">
          <span class="section-label">Booster Recovery</span>
          <div class="recovery-hero-number">
            {{ store.stats.total_landings }}
          </div>
          <p class="recovery-sub">
            successful landings · {{ store.stats.landing_success_rate }}% recovery rate
          </p>
          <span class="human-context">Out of every 10 boosters, ~{{ Math.round(store.stats.landing_success_rate / 10) }} land successfully. Each saves ~$50M in hardware.</span>
        </div>
        <div class="recovery-methods">
          <div class="surface method-cell">
            <span class="method-value">{{ store.stats.rtls_landings }}</span>
            <span class="method-label">
              RTLS Landings
              <InfoTip>Return to Launch Site — the booster flies back and lands at the launch pad.</InfoTip>
            </span>
            <span class="method-detail">{{ store.stats.rtls_attempts }} attempts</span>
          </div>
          <div class="surface method-cell">
            <span class="method-value">{{ store.stats.asds_landings }}</span>
            <span class="method-label">
              ASDS Landings
              <InfoTip>Autonomous Spaceport Drone Ship — the booster lands on a floating platform in the ocean.</InfoTip>
            </span>
            <span class="method-detail">{{ store.stats.asds_attempts }} attempts</span>
          </div>
          <div class="surface method-cell">
            <span class="method-value">{{ store.stats.active_cores }}</span>
            <span class="method-label">Active Boosters</span>
            <span class="method-detail">{{ store.stats.total_cores }} total</span>
          </div>
        </div>
      </div>

      <!-- Vehicle Success Chart -->
      <div
        v-if="store.rockets.length"
        class="surface section-gap"
      >
        <span class="section-label">Vehicle Success Rate</span>
        <RocketSuccessChart :data="store.rockets" />
      </div>

      <!-- Booster Reuse Leaderboard -->
      <div
        v-if="store.stats.most_reused.length"
        class="surface section-gap"
      >
        <span class="section-label">Booster Reuse Leaderboard</span>
        <CoreReuseChart :data="store.stats.most_reused" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFleetStore } from '@/stores/fleet'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ErrorState from '@/components/common/ErrorState.vue'
import RocketSuccessChart from '@/components/charts/RocketSuccessChart.vue'
import CoreReuseChart from '@/components/charts/CoreReuseChart.vue'
import InfoTip from '@/components/common/InfoTip.vue'

const router = useRouter()
const store = useFleetStore()
const expandedRocket = ref<string | null>(null)

function toggleRocket(id: string): void {
  expandedRocket.value = expandedRocket.value === id ? null : id
}

function goToRocket(id: string): void {
  router.push({ name: 'RocketDetail', params: { id } })
}

onMounted(() => {
  if (!store.stats) store.load()
})
</script>

<style scoped>
/* === ROCKET SHOWCASE === */
.rocket-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 8px;
}

.rocket-card {
  min-height: 200px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 2px solid transparent;
}

.rocket-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0,0,0,0.18);
}

.rocket-card.expanded {
  border-color: var(--accent);
}

.rocket-card-content {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 20px !important;
}

.rocket-expanded {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.rocket-detail-btn {
  flex-shrink: 0;
  padding: 8px 16px;
  background: var(--accent);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: opacity var(--transition);
  white-space: nowrap;
}

.rocket-detail-btn:hover {
  opacity: 0.85;
}

.expand-fade-enter-active,
.expand-fade-leave-active {
  transition: all 0.25s ease;
}

.expand-fade-enter-from,
.expand-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.rocket-status {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 3px;
}

.rocket-status.active {
  background: rgba(74, 222, 128, 0.15);
  color: var(--success);
}

.rocket-status.retired {
  background: rgba(82, 82, 91, 0.3);
  color: var(--text-muted);
}

.rocket-name {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  line-height: 1;
  margin-top: 4px;
}

.rocket-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 12px;
  margin-top: 10px;
}

.rocket-stat-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rocket-stat-val {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.rocket-stat-lbl {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.rocket-desc {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.5;
  flex: 1;
}

.cta-arrow {
  transition: transform 0.15s;
  display: inline-block;
}

.rocket-clickable:hover .cta-arrow {
  transform: translateX(3px);
}

/* === RECOVERY GRID === */
.recovery-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
}

.recovery-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.recovery-hero-number {
  font-family: var(--font-mono);
  font-size: 4rem;
  font-weight: 700;
  color: var(--success);
  line-height: 1;
  letter-spacing: -0.03em;
}

.recovery-sub {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 6px;
}

.recovery-methods {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.method-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.method-value {
  font-family: var(--font-mono);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}

.method-label {
  font-family: var(--font-display);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.method-detail {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .rocket-name { font-size: 1.8rem; }
  .rocket-card { min-height: 180px; }
  .recovery-grid { grid-template-columns: 1fr; }
  .recovery-hero-number { font-size: 2.8rem; }
  .recovery-methods { flex-direction: row; }
  .rocket-stats-grid { gap: 6px 10px; }
  .rocket-desc { max-width: 100%; }
}

@media (max-width: 640px) {
  .rocket-name { font-size: 1.4rem; }
  .rocket-card { min-height: 160px; }
  .rocket-showcase { grid-template-columns: 1fr; }
  .recovery-hero-number { font-size: 2.2rem; }
  .recovery-methods { flex-direction: column; }
  .rocket-stats-grid { gap: 4px 8px; }
  .rocket-stat-val { font-size: 0.95rem; }
  .rocket-expanded { flex-wrap: wrap; gap: 12px; }
  .rocket-detail-btn { white-space: normal; width: 100%; text-align: center; }
}
</style>
