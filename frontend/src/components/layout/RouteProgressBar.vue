<template>
  <Transition name="progress-fade">
    <div
      v-if="loading"
      class="route-progress"
    >
      <div
        class="route-progress-bar"
        :style="{ width: progress + '%' }"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const progress = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function start(): void {
  loading.value = true
  progress.value = 15

  timer = setInterval(() => {
    if (progress.value < 90) {
      progress.value += (90 - progress.value) * 0.1
    }
  }, 80)
}

function done(): void {
  progress.value = 100
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  setTimeout(() => {
    loading.value = false
    progress.value = 0
  }, 300)
}

let removeBeforeEach: (() => void) | null = null
let removeAfterEach: (() => void) | null = null

onMounted(() => {
  removeBeforeEach = router.beforeEach((_to, _from, next) => {
    start()
    next()
  })
  removeAfterEach = router.afterEach(() => {
    done()
  })
})

onUnmounted(() => {
  removeBeforeEach?.()
  removeAfterEach?.()
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.route-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 10000;
  pointer-events: none;
}

.route-progress-bar {
  height: 100%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent), 0 0 2px var(--accent);
  border-radius: 0 2px 2px 0;
  transition: width 0.2s ease;
}

.progress-fade-enter-active {
  transition: opacity 0.1s;
}

.progress-fade-leave-active {
  transition: opacity 0.3s ease 0.1s;
}

.progress-fade-enter-from,
.progress-fade-leave-to {
  opacity: 0;
}
</style>
