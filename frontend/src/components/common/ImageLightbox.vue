<template>
  <Teleport to="body">
    <Transition name="lightbox-fade">
      <div
        v-if="visible"
        ref="overlayRef"
        class="lightbox-overlay"
        role="dialog"
        aria-modal="true"
        aria-label="Image gallery"
        @click.self="close"
      >
        <!-- Close button -->
        <button
          ref="closeRef"
          class="lb-close"
          aria-label="Close"
          @click="close"
        >
          &times;
        </button>

        <!-- Counter -->
        <span class="lb-counter">{{ currentIndex + 1 }} / {{ images.length }}</span>

        <!-- Previous -->
        <button
          v-if="images.length > 1"
          class="lb-nav lb-prev"
          aria-label="Previous"
          @click="prev"
        >
          &#8249;
        </button>

        <!-- Image -->
        <img
          :src="images[currentIndex]"
          class="lb-image"
          alt="Gallery image"
          width="800"
          height="534"
          @click.stop
        >

        <!-- Next -->
        <button
          v-if="images.length > 1"
          class="lb-nav lb-next"
          aria-label="Next"
          @click="next"
        >
          &#8250;
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  images: string[]
  startIndex?: number
  visible?: boolean
}>(), {
  startIndex: 0,
  visible: false,
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
}>()

const currentIndex = ref(props.startIndex)
const overlayRef = ref<HTMLElement | null>(null)
const closeRef = ref<HTMLElement | null>(null)
let previouslyFocused: HTMLElement | null = null

watch(() => props.startIndex, (val) => {
  currentIndex.value = val
})

watch(() => props.visible, async (val) => {
  if (val) {
    currentIndex.value = props.startIndex
    document.body.style.overflow = 'hidden'
    previouslyFocused = document.activeElement as HTMLElement | null
    await nextTick()
    closeRef.value?.focus()
  } else {
    document.body.style.overflow = ''
    previouslyFocused?.focus()
    previouslyFocused = null
  }
})

function close(): void {
  emit('update:visible', false)
}

function next(): void {
  currentIndex.value = (currentIndex.value + 1) % props.images.length
}

function prev(): void {
  currentIndex.value = (currentIndex.value - 1 + props.images.length) % props.images.length
}

function trapFocus(e: KeyboardEvent): void {
  if (!overlayRef.value) return
  const focusable = overlayRef.value.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
  )
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (e.shiftKey) {
    if (document.activeElement === first) { e.preventDefault(); last.focus() }
  } else {
    if (document.activeElement === last) { e.preventDefault(); first.focus() }
  }
}

function onKeydown(e: KeyboardEvent): void {
  if (!props.visible) return
  if (e.key === 'Escape') close()
  else if (e.key === 'ArrowRight') next()
  else if (e.key === 'ArrowLeft') prev()
  else if (e.key === 'Tab') trapFocus(e)
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.lb-image {
  max-width: 90vw;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 6px;
  cursor: default;
  box-shadow: 0 8px 60px rgba(0, 0, 0, 0.6);
}

.lb-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 2.4rem;
  cursor: pointer;
  line-height: 1;
  padding: 4px 10px;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
  z-index: 2;
}

.lb-close:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.lb-counter {
  position: absolute;
  top: 24px;
  left: 24px;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 0.06em;
  pointer-events: none;
  z-index: 2;
}

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.75);
  font-size: 2.2rem;
  cursor: pointer;
  padding: 8px 14px;
  border-radius: 6px;
  line-height: 1;
  transition: background 0.15s, color 0.15s;
  z-index: 2;
}

.lb-nav:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.lb-prev { left: 20px; }
.lb-next { right: 20px; }

@media (max-width: 768px) {
  .lb-close { top: 12px; right: 12px; min-width: 48px; min-height: 48px; display: flex; align-items: center; justify-content: center; font-size: 2rem; }
  .lb-nav { padding: 12px 16px; min-width: 48px; min-height: 48px; font-size: 1.8rem; }
  .lb-prev { left: 8px; }
  .lb-next { right: 8px; }
  .lb-counter { top: 16px; left: 16px; }
  .lb-image { max-width: 95vw; max-height: 80vh; }
}

/* Transitions */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.25s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}
</style>
