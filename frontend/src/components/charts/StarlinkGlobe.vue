<template>
  <div
    ref="container"
    class="globe-container"
    role="img"
    aria-label="Starlink satellite constellation globe"
  >
    <canvas ref="canvas" />
    <div
      v-show="tooltipVisible"
      ref="tooltipEl"
      class="chart-tooltip globe-tooltip"
      :style="tooltipStyle"
    >
      <strong>{{ tooltipData.version }}</strong><br>
      Lat: {{ tooltipData.lat }}<br>
      Lng: {{ tooltipData.lng }}<br>
      Alt: {{ tooltipData.alt }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { StarlinkPosition } from '@/types'

const props = withDefaults(defineProps<{
  positions: StarlinkPosition[]
  activeVersions: Set<string>
  selectedSat: StarlinkPosition | null
  versionColorMap: Record<string, string>
}>(), {
  positions: () => [],
  activeVersions: () => new Set<string>(),
  selectedSat: null,
  versionColorMap: () => ({}),
})

const emit = defineEmits<{
  'visible-count': [count: number]
  'satellite-click': [sat: StarlinkPosition | null]
}>()

const container = ref<HTMLDivElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
const tooltipEl = ref<HTMLDivElement | null>(null)
const themeStore = useThemeStore()

const tooltipVisible = ref(false)
const tooltipStyle = reactive({ left: '0px', top: '0px' })
const tooltipData = reactive({ version: '', lat: '', lng: '', alt: '' })

let worldData: Record<string, unknown> | null = null
let animationId: number | null = null
let observer: ResizeObserver | null = null
let rotation: [number, number] = [0, -20]
let isDragging = false
let dragStart: [number, number] | null = null
let rotationStart: [number, number] | null = null
let velocity = 0.04
let zoomLevel = 1.3
let hoveredSat: StarlinkPosition | null = null
let mousePos: [number, number] | null = null

function getVersionColorMap(): Record<string, string> {
  if (props.versionColorMap && Object.keys(props.versionColorMap).length > 0) {
    return props.versionColorMap
  }
  const vars = ['--accent', '--accent-blue', '--accent-cyan', '--success', '--warning', '--text-secondary']
  const palette = vars.map((v) => getCssVar(v))
  const versions = [...new Set(props.positions.map((p) => p.version || 'unknown'))]
  const map: Record<string, string> = {}
  versions.forEach((v, i) => {
    map[v] = palette[i % palette.length]
  })
  return map
}

function getThemeColors() {
  const isDark = themeStore.theme === 'dark'
  return {
    ocean: isDark ? '#060610' : '#dce2ed',
    land: isDark ? '#12122a' : '#b8c2d6',
    landStroke: isDark ? '#1e1e40' : '#a0a8bc',
    border: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
    glow: isDark ? 'rgba(91,141,239,0.12)' : 'rgba(59,111,212,0.06)',
    highlight: isDark ? '#ffffff' : '#18181b',
  }
}

async function loadWorld(): Promise<Record<string, unknown>> {
  if (worldData) return worldData
  const resp = await fetch('/data/world-110m.json')
  worldData = await resp.json()
  return worldData!
}

function render() {
  if (!container.value || !canvas.value || !worldData) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight || 420
  const dpr = window.devicePixelRatio || 1

  canvas.value.width = width * dpr
  canvas.value.height = height * dpr
  canvas.value.style.width = width + 'px'
  canvas.value.style.height = height + 'px'

  const ctx = canvas.value.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const baseRadius = Math.min(width, height) / 2 - 20
  const radius = baseRadius * zoomLevel
  const projection = d3.geoOrthographic()
    .scale(radius)
    .translate([width / 2, height / 2])
    .rotate(rotation)
    .clipAngle(90)

  const path = d3.geoPath(projection, ctx)
  const colors = getThemeColors()
  const versionMap = getVersionColorMap()
  const land = topojson.feature(worldData, worldData.objects.countries)

  ctx.clearRect(0, 0, width, height)

  // Outer glow
  const gradient = ctx.createRadialGradient(width / 2, height / 2, radius * 0.9, width / 2, height / 2, radius * 1.2)
  gradient.addColorStop(0, colors.glow)
  gradient.addColorStop(1, 'transparent')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  // Ocean sphere
  ctx.beginPath()
  path({ type: 'Sphere' })
  ctx.fillStyle = colors.ocean
  ctx.fill()
  ctx.strokeStyle = colors.border
  ctx.lineWidth = 0.5
  ctx.stroke()

  // Land
  ctx.beginPath()
  path(land)
  ctx.fillStyle = colors.land
  ctx.fill()
  ctx.strokeStyle = colors.landStroke
  ctx.lineWidth = 0.3
  ctx.stroke()

  // Graticule
  const graticule = d3.geoGraticule().step([30, 30])()
  ctx.beginPath()
  path(graticule)
  ctx.strokeStyle = colors.border
  ctx.lineWidth = 0.15
  ctx.stroke()

  // Satellites
  let visibleCount = 0
  const dotRadius = Math.min(1.8 * zoomLevel, 4)
  const haloRadius = Math.min(3.5 * zoomLevel, 7)
  const hasFilter = props.activeVersions.size > 0

  if (props.positions.length > 0) {
    // First pass: halos
    for (const sat of props.positions) {
      const ver = sat.version || 'unknown'
      if (hasFilter && !props.activeVersions.has(ver)) continue

      const coords = [sat.longitude, sat.latitude]
      const dist = d3.geoDistance(coords, [-rotation[0], -rotation[1]])
      if (dist > Math.PI / 2) continue

      const point = projection(coords)
      if (!point) continue

      const color = versionMap[ver] || getCssVar('--accent')

      // Halo glow
      ctx.beginPath()
      ctx.arc(point[0], point[1], haloRadius, 0, 2 * Math.PI)
      ctx.fillStyle = color
      ctx.globalAlpha = 0.2
      ctx.fill()
      ctx.globalAlpha = 1
    }

    // Second pass: solid dots + count
    for (const sat of props.positions) {
      const ver = sat.version || 'unknown'
      if (hasFilter && !props.activeVersions.has(ver)) continue

      const coords = [sat.longitude, sat.latitude]
      const dist = d3.geoDistance(coords, [-rotation[0], -rotation[1]])
      if (dist > Math.PI / 2) continue

      const point = projection(coords)
      if (!point) continue

      visibleCount++
      const color = versionMap[ver] || getCssVar('--accent')

      ctx.beginPath()
      ctx.arc(point[0], point[1], dotRadius, 0, 2 * Math.PI)
      ctx.fillStyle = color
      ctx.fill()
    }

    // Highlight selected satellite (permanent)
    const activeSat = props.selectedSat || hoveredSat
    if (activeSat) {
      const coords = [activeSat.longitude, activeSat.latitude]
      const dist = d3.geoDistance(coords, [-rotation[0], -rotation[1]])
      if (dist <= Math.PI / 2) {
        const point = projection(coords)
        if (point) {
          // Outer pulse ring
          if (props.selectedSat) {
            ctx.beginPath()
            ctx.arc(point[0], point[1], 8 * zoomLevel, 0, 2 * Math.PI)
            ctx.strokeStyle = colors.highlight
            ctx.globalAlpha = 0.15
            ctx.lineWidth = 2
            ctx.stroke()
            ctx.globalAlpha = 1
          }
          // Inner highlight ring
          ctx.beginPath()
          ctx.arc(point[0], point[1], 5 * zoomLevel, 0, 2 * Math.PI)
          ctx.strokeStyle = colors.highlight
          ctx.lineWidth = 1.5
          ctx.stroke()
        }
      }
    }
  }

  emit('visible-count', visibleCount)
}

function findNearestSatellite(mx: number, my: number): StarlinkPosition | null {
  if (!container.value || !canvas.value || !worldData || props.positions.length === 0) return null

  const width = container.value.clientWidth
  const height = container.value.clientHeight || 420
  const baseRadius = Math.min(width, height) / 2 - 20
  const radius = baseRadius * zoomLevel
  const projection = d3.geoOrthographic()
    .scale(radius)
    .translate([width / 2, height / 2])
    .rotate(rotation)
    .clipAngle(90)

  const hasFilter = props.activeVersions.size > 0
  let closest = null
  let minDist = 10 // max pixel distance for hit

  for (const sat of props.positions) {
    const ver = sat.version || 'unknown'
    if (hasFilter && !props.activeVersions.has(ver)) continue

    const coords = [sat.longitude, sat.latitude]
    const dist = d3.geoDistance(coords, [-rotation[0], -rotation[1]])
    if (dist > Math.PI / 2) continue

    const point = projection(coords)
    if (!point) continue

    const dx = point[0] - mx
    const dy = point[1] - my
    const d = Math.sqrt(dx * dx + dy * dy)
    if (d < minDist) {
      minDist = d
      closest = sat
    }
  }
  return closest
}

function animate() {
  if (!isDragging && !props.selectedSat) {
    rotation[0] += velocity
  }
  render()
  animationId = requestAnimationFrame(animate)
}

function setupInteractions() {
  const el = canvas.value
  if (!el) return

  // Drag
  el.addEventListener('pointerdown', (e: PointerEvent) => {
    isDragging = true
    dragStart = [e.clientX, e.clientY]
    rotationStart = [...rotation] as [number, number]
    el.setPointerCapture(e.pointerId)
    tooltipVisible.value = false
    hoveredSat = null
  })

  el.addEventListener('pointermove', (e: PointerEvent) => {
    const rect = el.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    mousePos = [mx, my]

    if (isDragging && dragStart) {
      const dx = e.clientX - dragStart[0]
      const dy = e.clientY - dragStart[1]
      const sensitivity = 0.3
      rotation[0] = rotationStart[0] + dx * sensitivity
      rotation[1] = Math.max(-60, Math.min(60, rotationStart[1] - dy * sensitivity))
      return
    }

    // Hover detection
    const sat = findNearestSatellite(mx, my)
    if (sat) {
      hoveredSat = sat
      tooltipData.version = sat.version || 'Unknown'
      tooltipData.lat = sat.latitude.toFixed(2) + '°'
      tooltipData.lng = sat.longitude.toFixed(2) + '°'
      tooltipData.alt = sat.height_km ? sat.height_km.toLocaleString() + ' km' : '—'
      tooltipStyle.left = (mx + 14) + 'px'
      tooltipStyle.top = (my - 14) + 'px'
      tooltipVisible.value = true
      el.style.cursor = 'crosshair'
    } else {
      hoveredSat = null
      tooltipVisible.value = false
      el.style.cursor = isDragging ? 'grabbing' : 'grab'
    }
  })

  el.addEventListener('pointerup', (e: PointerEvent) => {
    const wasDrag = dragStart && (
      Math.abs(e.clientX - dragStart[0]) > 5 || Math.abs(e.clientY - dragStart[1]) > 5
    ) as boolean
    isDragging = false
    dragStart = null
    rotationStart = null

    // If it was a click (not a drag), find and emit satellite
    if (!wasDrag && mousePos) {
      const sat = findNearestSatellite(mousePos[0], mousePos[1])
      emit('satellite-click', sat) // null if no satellite nearby (clears selection)
    }
  })

  el.addEventListener('pointercancel', () => {
    isDragging = false
    dragStart = null
    rotationStart = null
  })

  el.addEventListener('pointerleave', () => {
    hoveredSat = null
    tooltipVisible.value = false
  })

  // Zoom
  el.addEventListener('wheel', (e: WheelEvent) => {
    e.preventDefault()
    const delta = -e.deltaY * 0.001
    zoomLevel = Math.max(0.5, Math.min(3.0, zoomLevel + delta))
  }, { passive: false })
}

onMounted(async () => {
  await loadWorld()
  render()
  setupInteractions()
  animate()
  observer = new ResizeObserver(() => render())
  observer.observe(container.value)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  observer?.disconnect()
})

watch(() => themeStore.theme, () => render())
watch(() => props.positions, () => render(), { deep: true })
watch(() => props.activeVersions, () => render(), { deep: true })
watch(() => props.versionColorMap, () => render(), { deep: true })
watch(() => props.selectedSat, () => render())
</script>

<style scoped>
.globe-container {
  width: 100%;
  height: 420px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
}

.globe-container:active {
  cursor: grabbing;
}

canvas {
  display: block;
}

.globe-tooltip {
  position: absolute;
  z-index: 60;
  pointer-events: none;
}
</style>
