<template>
  <div
    class="notif-container"
    aria-live="polite"
  >
    <TransitionGroup
      name="notif"
      tag="div"
    >
      <div
        v-for="n in store.notifications"
        :key="n.id"
        class="notif-toast"
        :class="'notif-' + n.type"
        role="alert"
      >
        <span class="notif-icon">
          <svg
            viewBox="0 0 16 16"
            width="15"
            height="15"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            aria-hidden="true"
          >
            <path :d="iconPath(n.type)" />
          </svg>
        </span>
        <div class="notif-body">
          <span class="notif-label">{{ n.type }}</span>
          <p class="notif-title">
            {{ n.title }}
          </p>
          <p class="notif-message">
            {{ n.message }}
          </p>
        </div>
        <button
          class="notif-close"
          aria-label="Dismiss notification"
          @click="store.dismiss(n.id)"
        >
          &times;
        </button>
        <span
          class="notif-progress"
          :style="{ animationDuration: dismissMs(n.type) + 'ms' }"
        />
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notifications'

const store = useNotificationStore()

const icons: Record<string, string> = {
  success: 'M3 8.5l3.5 3.5 6.5-7',
  warning: 'M8 1l7 14H1L8 1zM8 6v4M8 12v.01',
  error: 'M4 4l8 8M12 4l-8 8',
  info: 'M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zM8 5v.01M8 7v5',
  launch: 'M8 1v8M5 6l3-5 3 5M4 14c0-3 2-5 4-5s4 2 4 5',
}

const durations: Record<string, number> = {
  error: 12000,
  warning: 10000,
  success: 8000,
  info: 8000,
  launch: 10000,
}

function iconPath(type: string): string {
  return icons[type] || icons.info
}

function dismissMs(type: string): number {
  return durations[type] ?? 8000
}
</script>

<style scoped>
.notif-container {
  position: fixed;
  top: 64px;
  right: 16px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  max-width: 380px;
  width: 100%;
}

.notif-toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 36px 12px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-left: 3px solid var(--text-muted);
  border-radius: var(--radius);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
  overflow: hidden;
}

/* Type colors for left border */
.notif-success { border-left-color: var(--success); }
.notif-warning { border-left-color: var(--warning); }
.notif-error { border-left-color: var(--error); }
.notif-info { border-left-color: var(--accent-cyan); }
.notif-launch { border-left-color: var(--accent); }

/* Icon */
.notif-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 1px;
}

.notif-success .notif-icon { color: var(--success); background: color-mix(in srgb, var(--success) 12%, transparent); }
.notif-warning .notif-icon { color: var(--warning); background: color-mix(in srgb, var(--warning) 12%, transparent); }
.notif-error .notif-icon { color: var(--error); background: color-mix(in srgb, var(--error) 12%, transparent); }
.notif-info .notif-icon { color: var(--accent-cyan); background: color-mix(in srgb, var(--accent-cyan) 12%, transparent); }
.notif-launch .notif-icon { color: var(--accent); background: var(--accent-dim); }

/* Body */
.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-label {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.notif-title {
  font-family: var(--font-display);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.3;
  margin-top: 2px;
}

.notif-message {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-top: 2px;
}

/* Close button */
.notif-close {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 2px 5px;
  border-radius: 3px;
  transition: color 0.12s, background 0.12s;
}

.notif-close:hover {
  color: var(--text);
  background: var(--bg-hover);
}

/* Progress bar */
.notif-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 100%;
  transform-origin: left;
  animation: notif-shrink linear forwards;
}

.notif-success .notif-progress { background: var(--success); }
.notif-warning .notif-progress { background: var(--warning); }
.notif-error .notif-progress { background: var(--error); }
.notif-info .notif-progress { background: var(--accent-cyan); }
.notif-launch .notif-progress { background: var(--accent); }

@keyframes notif-shrink {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Transition */
.notif-enter-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.notif-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.notif-enter-from {
  opacity: 0;
  transform: translateX(60px);
}

.notif-leave-to {
  opacity: 0;
  transform: translateX(60px) scale(0.95);
}

.notif-move {
  transition: transform 0.3s ease;
}

/* Responsive */
@media (max-width: 640px) {
  .notif-container {
    top: 56px;
    right: 0;
    left: 0;
    max-width: 100%;
    padding: 0 8px;
  }
}
</style>
