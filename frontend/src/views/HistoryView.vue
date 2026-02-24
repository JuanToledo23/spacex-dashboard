<template>
  <section class="history-page">
    <header class="history-header">
      <span class="header-tag">MILESTONES</span>
      <h1>SpaceX History</h1>
      <p
        v-if="data"
        class="header-sub"
      >
        {{ data.total }} key moments that shaped the future of spaceflight
      </p>
    </header>

    <div
      v-if="loading"
      class="loading-state"
    >
      <SkeletonLoader
        variant="text"
        :count="3"
      />
      <div style="display: flex; flex-direction: column; gap: 20px; margin-top: 20px; max-width: 600px">
        <SkeletonLoader
          variant="stat"
          :count="5"
        />
      </div>
    </div>

    <div
      v-else-if="data"
      class="timeline"
    >
      <div class="timeline-line" />

      <article
        v-for="(event, idx) in data.events"
        :key="event.id"
        class="timeline-item"
        :class="idx % 2 === 0 ? 'left' : 'right'"
      >
        <div class="timeline-dot" />
        <div class="timeline-card surface">
          <time class="event-date">{{ formatDate(event.event_date_utc) }}</time>
          <h2 class="event-title">
            {{ event.title }}
          </h2>
          <p
            v-if="event.details"
            class="event-details"
          >
            {{ event.details }}
          </p>
          <div
            v-if="event.article || event.wikipedia"
            class="event-links"
          >
            <a
              v-if="event.article"
              :href="event.article"
              target="_blank"
              rel="noopener"
              class="event-link"
            >
              Read Article &rarr;
            </a>
            <a
              v-if="event.wikipedia"
              :href="event.wikipedia"
              target="_blank"
              rel="noopener"
              class="event-link wiki-link"
            >
              Wikipedia
            </a>
          </div>
        </div>
      </article>
    </div>

    <ErrorState
      v-else
      message="Unable to load history data."
      @retry="loadData"
    />
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchHistory } from '@/api'
import { formatDate } from '@/utils/formatDate'
import ErrorState from '@/components/common/ErrorState.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import type { HistoryResponse } from '@/types'

const data = ref<HistoryResponse | null>(null)
const loading = ref(true)

async function loadData(): Promise<void> {
  loading.value = true
  data.value = null
  try {
    data.value = await fetchHistory()
  } catch (e) {
    console.error('Failed to fetch history:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.history-page {
  max-width: 960px;
  margin: 0 auto;
}

.history-header {
  text-align: center;
  margin-bottom: 56px;
}

.header-tag {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--accent);
  letter-spacing: 0.14em;
  display: block;
  margin-bottom: 8px;
}

.history-header h1 {
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

/* Timeline structure */
.timeline {
  position: relative;
  padding: 24px 0;
}

.timeline-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--border-strong);
  transform: translateX(-50%);
}

.timeline-item {
  position: relative;
  display: flex;
  width: 50%;
  padding: 0 40px;
  margin-bottom: 36px;
}

.timeline-item.left {
  justify-content: flex-end;
  padding-right: 40px;
  padding-left: 0;
}

.timeline-item.right {
  margin-left: 50%;
  padding-left: 40px;
  padding-right: 0;
}

/* Dot on timeline */
.timeline-dot {
  position: absolute;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--bg-base);
  top: 20px;
  z-index: 2;
}

.timeline-item.left .timeline-dot {
  right: -6px;
}

.timeline-item.right .timeline-dot {
  left: -6px;
}

/* Card */
.timeline-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  max-width: 400px;
  width: 100%;
  transition: border-color 0.2s;
}

.timeline-card:hover {
  border-color: var(--accent);
}

.event-date {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--accent);
  letter-spacing: 0.04em;
  display: block;
  margin-bottom: 8px;
}

.event-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 10px;
  line-height: 1.3;
}

.event-details {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0 0 14px;
}

.event-links {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.event-link {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.15s;
}

.event-link:hover {
  border-bottom-color: var(--accent);
}

.wiki-link {
  color: var(--accent-blue);
}

.wiki-link:hover {
  border-bottom-color: var(--accent-blue);
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
}

/* Responsive: single column on mobile */
@media (max-width: 768px) {
  .timeline-line {
    left: 20px;
  }

  .timeline-item,
  .timeline-item.left,
  .timeline-item.right {
    width: 100%;
    margin-left: 0;
    padding-left: 48px;
    padding-right: 0;
    justify-content: flex-start;
  }

  .timeline-item.left .timeline-dot,
  .timeline-item.right .timeline-dot {
    left: 15px;
    right: auto;
  }

  .timeline-card {
    max-width: 100%;
  }
  .history-page { padding: 0; }
  .history-header { margin-bottom: 36px; }
  .history-header h1 { font-size: 1.8rem; }
}

@media (max-width: 640px) {
  .history-page { padding: 0; }
  .history-header h1 { font-size: 1.4rem; }
  .event-title { font-size: 1.05rem; }
  .timeline-item { margin-bottom: 24px; }
  .timeline-item.left,
  .timeline-item.right { padding-left: 36px; }
  .timeline-line { left: 14px; }
  .timeline-item.left .timeline-dot,
  .timeline-item.right .timeline-dot { left: 9px; }
}
</style>
