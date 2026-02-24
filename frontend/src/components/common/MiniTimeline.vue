<template>
  <div class="timeline">
    <div
      v-for="(item, i) in items"
      :key="item.id"
      class="tl-item"
    >
      <div class="tl-line">
        <div
          class="tl-marker"
          :class="item.success === true ? 'ok' : item.success === false ? 'err' : 'pending'"
        />
        <div
          v-if="i < items.length - 1"
          class="tl-connector"
        />
      </div>
      <div class="tl-patch">
        <img
          v-if="item.patch_small"
          :src="item.patch_small"
          class="tl-patch-img"
          :alt="item.name + ' mission patch'"
          width="28"
          height="28"
        >
        <svg
          v-else
          class="tl-patch-fallback"
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            cx="12"
            cy="12"
            r="11"
            stroke="currentColor"
            stroke-width="0.8"
            opacity="0.2"
          />
          <path
            d="M12 4 L14 10 L12 20 L10 10 Z"
            fill="currentColor"
            opacity="0.25"
          />
        </svg>
      </div>
      <div class="tl-content">
        <div class="tl-header">
          <span class="tl-name">{{ item.name }}</span>
          <div class="tl-actions">
            <a
              v-if="item.webcast"
              :href="item.webcast"
              target="_blank"
              rel="noopener"
              class="tl-webcast"
              title="Watch on YouTube"
            ><svg
              class="yt-icon"
              viewBox="0 0 28 20"
              fill="none"
              aria-hidden="true"
            ><rect
              width="28"
              height="20"
              rx="4"
              fill="#FF0000"
            /><path
              d="M11 5.5L19 10L11 14.5V5.5Z"
              fill="#FFF"
            /></svg></a>
            <span
              class="tl-result"
              :class="item.success === true ? 'ok' : item.success === false ? 'err' : ''"
            >
              {{ item.success === true ? 'OK' : item.success === false ? 'FAIL' : '—' }}
            </span>
          </div>
        </div>
        <div class="tl-meta">
          <span
            v-if="item.rocket_name"
            class="tl-rocket"
          >{{ item.rocket_name }}</span>
          <span class="tl-date">{{ formatDate(item.date_utc) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDateShort as formatDate } from '@/utils/formatDate'
import type { LaunchHighlight } from '@/types'

defineProps<{
  items: LaunchHighlight[]
}>()
</script>

<style scoped>
.timeline { display: flex; flex-direction: column; }

.tl-item { display: flex; gap: 10px; }

.tl-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 10px;
}

.tl-marker {
  width: 6px;
  height: 6px;
  border-radius: 1px;
  flex-shrink: 0;
  margin-top: 6px;
  transform: rotate(45deg);
}

.tl-marker.ok { background: var(--success); }
.tl-marker.err { background: var(--error); }
.tl-marker.pending { background: var(--text-muted); }

.tl-connector {
  width: 1px;
  flex: 1;
  min-height: 16px;
  background: var(--border);
}

.tl-patch {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  margin-top: 1px;
}

.tl-patch-img {
  width: 26px;
  height: 26px;
  object-fit: contain;
  opacity: 0.85;
}

.tl-patch-fallback {
  width: 26px;
  height: 26px;
  color: var(--text-muted);
  opacity: 0.5;
}

.tl-content {
  flex: 1;
  min-width: 0;
  padding-bottom: 14px;
}

.tl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 2px;
}

.tl-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.tl-webcast {
  display: flex;
  align-items: center;
  text-decoration: none;
  opacity: 0.65;
  transition: opacity 0.15s, transform 0.15s;
  line-height: 1;
}

.tl-webcast:hover {
  opacity: 1;
  transform: scale(1.1);
}

.yt-icon {
  width: 18px;
  height: 13px;
}

.tl-name {
  font-family: var(--font-display);
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tl-result {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  flex-shrink: 0;
}

.tl-result.ok { color: var(--success); }
.tl-result.err { color: var(--error); }

.tl-meta {
  display: flex;
  gap: 10px;
  font-size: 0.85rem;
}

.tl-rocket {
  color: var(--accent);
  font-family: var(--font-mono);
}

.tl-date {
  color: var(--text-muted);
  font-family: var(--font-mono);
}

@media (max-width: 640px) {
  .tl-item { gap: 8px; }
  .tl-header { flex-wrap: wrap; }
  .tl-name { font-size: 0.85rem; }
  .tl-meta { font-size: 0.78rem; gap: 8px; }
  .yt-icon { width: 16px; height: 11px; }
  .tl-result { font-size: 0.72rem; }
}
</style>
