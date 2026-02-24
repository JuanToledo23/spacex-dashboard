<template>
  <span
    class="info-tip"
    tabindex="0"
    role="button"
    :aria-expanded="show"
    @mouseenter="show = true"
    @mouseleave="show = false"
    @focus="show = true"
    @blur="show = false"
    @click.stop="show = !show"
  >
    <span
      class="info-tip-icon"
      aria-hidden="true"
    >i</span>
    <Transition name="tip-fade">
      <span
        v-if="show"
        class="info-tip-popup"
        role="tooltip"
      >
        <slot />
      </span>
    </Transition>
  </span>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const show = ref(false)
</script>

<style scoped>
.info-tip {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  vertical-align: middle;
  cursor: help;
}

.info-tip-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--text-muted);
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 0.6rem;
  font-weight: 700;
  font-style: italic;
  line-height: 1;
  transition: all var(--transition);
  flex-shrink: 0;
}

.info-tip:hover .info-tip-icon,
.info-tip:focus .info-tip-icon {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-dim);
}

.info-tip-popup {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 200px;
  max-width: 280px;
  padding: 10px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.8rem;
  font-style: normal;
  font-weight: 400;
  line-height: 1.5;
  white-space: normal;
  text-transform: none;
  letter-spacing: normal;
  z-index: 100;
  pointer-events: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.info-tip-popup::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--border-strong);
}

.tip-fade-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.tip-fade-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.tip-fade-enter-from,
.tip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}

@media (max-width: 640px) {
  .info-tip {
    min-width: 44px;
    min-height: 44px;
    justify-content: center;
  }

  .info-tip-popup {
    position: fixed;
    bottom: auto;
    top: auto;
    left: 16px;
    right: 16px;
    transform: none;
    min-width: auto;
    max-width: none;
    font-size: 0.85rem;
  }

  .info-tip-popup::after { display: none; }
}
</style>
