<template>
  <Transition name="lab-fade">
    <div
      v-if="store.open"
      class="lab-overlay"
      @click.self="store.close()"
    >
      <div
        class="lab-panel surface"
        role="dialog"
        aria-labelledby="error-lab-title"
        aria-describedby="error-lab-desc"
      >
        <div class="lab-header">
          <h2
            id="error-lab-title"
            class="lab-title"
          >
            Error Testing Lab
          </h2>
          <button
            class="lab-close"
            aria-label="Close panel"
            @click="store.close()"
          >
            &times;
          </button>
        </div>
        <p
          id="error-lab-desc"
          class="lab-desc"
        >
          Trigger simulated errors to see how the dashboard handles them.
        </p>

        <div class="lab-section">
          <span class="lab-label">Inline error (ErrorState)</span>
          <button
            class="lab-btn"
            @click="triggerErrorState"
          >
            Show ErrorState
          </button>
        </div>

        <div class="lab-section">
          <span class="lab-label">Toast notification</span>
          <button
            class="lab-btn"
            @click="triggerToast"
          >
            Show error toast
          </button>
        </div>

        <div class="lab-section">
          <span class="lab-label">API errors (via backend)</span>
          <div class="lab-btn-row">
            <button
              v-for="code in apiCodes"
              :key="code"
              class="lab-btn lab-btn-sm"
              @click="triggerApiError(code)"
            >
              {{ code }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useNotificationStore } from '@/stores/notifications'
import { useErrorLabStore } from '@/stores/errorLab'
import { triggerError } from '@/api'
import { extractErrorMessage } from '@/utils/handleError'

const router = useRouter()
const dashboardStore = useDashboardStore()
const notificationStore = useNotificationStore()
const store = useErrorLabStore()

const apiCodes = ['404', '500', '502', '503', 'timeout']

function triggerErrorState() {
  dashboardStore.$patch({
    error: 'Simulated error for demo — click RETRY to recover',
    data: null,
  })
  router.push('/')
  store.close()
}

function triggerToast() {
  notificationStore.add({
    id: crypto.randomUUID(),
    type: 'error',
    title: 'Demo: Error Toast',
    message: 'This is a simulated error notification. It auto-dismisses after 12 seconds.',
    timestamp: new Date().toISOString(),
  })
}

async function triggerApiError(code: string) {
  try {
    await triggerError(code)
  } catch (err) {
    const msg = extractErrorMessage(err, `Simulated ${code} error`)
    dashboardStore.$patch({ error: msg, data: null })
    router.push('/')
    store.close()
  }
}
</script>

<style scoped>
.lab-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.lab-panel {
  max-width: 420px;
  width: 100%;
  padding: 24px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-strong);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

.lab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.lab-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.04em;
}

.lab-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius);
  transition: color 0.12s, background 0.12s;
}

.lab-close:hover {
  color: var(--text);
  background: var(--bg-hover);
}

.lab-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 20px;
}

.lab-section {
  margin-bottom: 16px;
}

.lab-section:last-child {
  margin-bottom: 0;
}

.lab-label {
  display: block;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.lab-btn {
  display: block;
  width: 100%;
  padding: 10px 16px;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text);
  background: var(--bg-hover);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}

.lab-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--text-muted);
}

.lab-btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lab-btn-sm {
  flex: 1;
  min-width: 76px;
  white-space: nowrap;
}

.lab-fade-enter-active,
.lab-fade-leave-active {
  transition: opacity 0.2s ease;
}

.lab-fade-enter-from,
.lab-fade-leave-to {
  opacity: 0;
}

.lab-fade-enter-active .lab-panel,
.lab-fade-leave-active .lab-panel {
  transition: transform 0.2s ease;
}

.lab-fade-enter-from .lab-panel,
.lab-fade-leave-to .lab-panel {
  transform: scale(0.96);
}
</style>
