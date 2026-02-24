<template>
  <div class="error-panel surface">
    <span class="error-label">ERROR</span>
    <p class="error-msg">
      {{ message }}
    </p>
    <button
      class="error-btn"
      :disabled="retrying"
      @click="$emit('retry')"
    >
      <span
        v-if="retrying"
        class="error-spinner"
      />
      {{ retrying ? 'RETRYING...' : 'RETRY' }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  message?: string
  retrying?: boolean
}>(), {
  message: 'Something went wrong. Please try again.',
  retrying: false,
})

defineEmits<{
  'retry': []
}>()
</script>

<style scoped>
.error-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 20px;
  gap: 12px;
}

.error-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.15em;
  color: var(--error);
}

.error-msg {
  color: var(--text-secondary);
  font-size: 0.82rem;
  max-width: 380px;
}

.error-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  padding: 8px 20px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  transition: all var(--transition);
}

.error-btn:hover:not(:disabled) {
  background: var(--text);
  color: var(--text-inverse);
  border-color: var(--text);
}

.error-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid var(--text-muted);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@media (max-width: 768px) {
  .error-btn { min-height: 44px; padding: 10px 24px; font-size: 0.78rem; }
  .error-panel { padding: 32px 16px; }
}
</style>
