<template>
  <nav
    ref="navEl"
    class="section-nav"
    :class="{ stuck: isStuck }"
    aria-label="Page sections"
  >
    <div class="section-nav-inner">
      <button
        v-for="item in sections"
        :key="item.id"
        class="section-pill"
        :class="{ active: activeId === item.id }"
        @click="scrollTo(item.id)"
      >
        {{ item.label }}
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

export interface SectionItem {
  id: string
  label: string
}

defineProps<{ sections: SectionItem[] }>()

const navEl = ref<HTMLElement | null>(null)
const activeId = ref('')
const isStuck = ref(false)

let observer: IntersectionObserver | null = null
let sentinelEl: HTMLElement | null = null

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const headerH = 52
  const navH = navEl.value?.offsetHeight ?? 44
  const y = el.getBoundingClientRect().top + window.scrollY - headerH - navH - 8
  window.scrollTo({ top: y, behavior: 'smooth' })
}

function setupStickyDetection() {
  if (!navEl.value) return
  sentinelEl = document.createElement('div')
  sentinelEl.style.height = '1px'
  sentinelEl.style.marginBottom = '-1px'
  sentinelEl.setAttribute('aria-hidden', 'true')
  navEl.value.parentNode?.insertBefore(sentinelEl, navEl.value)

  const stickyObs = new IntersectionObserver(
    ([entry]) => { isStuck.value = !entry.isIntersecting },
    { threshold: 0 },
  )
  stickyObs.observe(sentinelEl)
}

function setupScrollSpy() {
  const headerH = 52
  const navH = 48
  const offset = headerH + navH + 24

  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeId.value = entry.target.id
        }
      }
    },
    { rootMargin: `-${offset}px 0px -60% 0px`, threshold: 0 },
  )

  const targets = document.querySelectorAll('[data-section-nav]')
  targets.forEach((t) => observer?.observe(t))
}

onMounted(() => {
  setupStickyDetection()
  setupScrollSpy()
})

onUnmounted(() => {
  observer?.disconnect()
  sentinelEl?.remove()
})
</script>

<style scoped>
.section-nav {
  position: sticky;
  top: 52px;
  z-index: 40;
  background: var(--bg-base);
  padding: 8px 0;
  transition: box-shadow 0.2s ease;
  margin-bottom: 16px;
}

.section-nav.stuck {
  box-shadow: 0 1px 0 var(--border);
}

.section-nav-inner {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 0 2px;
}

.section-nav-inner::-webkit-scrollbar {
  display: none;
}

.section-pill {
  flex-shrink: 0;
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.section-pill:hover {
  color: var(--text);
  border-color: var(--border-strong);
}

.section-pill.active {
  color: var(--text);
  background: var(--bg-surface);
  border-color: var(--border-strong);
}

@media (max-width: 640px) {
  .section-pill {
    padding: 8px 12px;
    font-size: 0.68rem;
    min-height: 36px;
  }
}
</style>
