<template>
  <Transition name="funfact-slide">
    <div
      v-if="visible"
      class="funfact-bar"
    >
      <div class="funfact-content">
        <svg
          class="funfact-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          width="18"
          height="18"
          aria-hidden="true"
        >
          <path d="M9.663 17h4.674M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <span class="funfact-label">Did you know?</span>
        <span class="funfact-text">{{ fact }}</span>
        <button
          class="funfact-close"
          aria-label="Close"
          @click="dismiss"
        >
          &times;
        </button>
      </div>
      <div
        class="funfact-progress"
        :style="{ animationDuration: `${duration}ms` }"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { fetchFunFact } from '@/api'

const visible = ref(false)
const fact = ref('')
const duration = 12000

let dismissTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  try {
    const res = await fetchFunFact()
    if (res.fact) {
      fact.value = res.fact
      visible.value = true
      dismissTimer = setTimeout(dismiss, duration)
    }
  } catch {
    // AI not available or failed — silently skip
  }
})

onBeforeUnmount(() => {
  if (dismissTimer) clearTimeout(dismissTimer)
})

function dismiss(): void {
  visible.value = false
  if (dismissTimer) {
    clearTimeout(dismissTimer)
    dismissTimer = null
  }
}
</script>

<style scoped>
.funfact-bar {
  position: fixed;
  top: 56px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 80;
  width: 92%;
  max-width: 680px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.funfact-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
}

.funfact-icon {
  flex-shrink: 0;
  color: var(--accent);
}

.funfact-label {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent);
  white-space: nowrap;
}

.funfact-text {
  flex: 1;
  font-size: 0.85rem;
  line-height: 1.45;
  color: var(--text-secondary);
}

.funfact-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.12s, background 0.12s;
}

.funfact-close:hover {
  color: var(--text);
  background: var(--bg-hover);
}

/* Progress bar that shrinks over the duration */
.funfact-progress {
  height: 2px;
  background: var(--accent);
  animation: funfact-shrink linear forwards;
  transform-origin: left;
}

@keyframes funfact-shrink {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Slide transition */
.funfact-slide-enter-active {
  transition: transform 0.4s ease, opacity 0.4s ease;
}

.funfact-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.funfact-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.funfact-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

/* Responsive */
@media (max-width: 640px) {
  .funfact-bar {
    top: 52px;
    width: 96%;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  }

  .funfact-content {
    padding: 10px 12px;
    gap: 8px;
  }

  .funfact-label {
    display: none;
  }

  .funfact-text {
    font-size: 0.8rem;
  }
}
</style>
