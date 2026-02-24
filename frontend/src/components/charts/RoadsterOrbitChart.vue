<template>
  <div
    ref="container"
    class="orbit-chart"
    role="img"
    aria-label="Tesla Roadster orbital path visualization"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { getCssVar } from '@/utils/chartColors'
import { useThemeStore } from '@/stores/theme'

const props = withDefaults(defineProps<{
  apoapsis?: number
  periapsis?: number
  semiMajorAxis?: number
}>(), {
  apoapsis: 1.664,
  periapsis: 0.986,
  semiMajorAxis: 1.325,
})

const themeStore = useThemeStore()
const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null
let animId: number | null = null

function draw() {
  if (!svg.value || !container.value) return

  // Cancel previous animation
  if (animId) cancelAnimationFrame(animId)

  const el = container.value
  const width = el.clientWidth
  const legendHeight = 40
  const height = Math.min(width * 0.75, 500) + legendHeight

  const s = d3.select(svg.value)
  s.selectAll('*').remove()
  s.attr('width', width).attr('height', height)

  const accentBlue = getCssVar('--accent-blue') || '#5b8def'
  const textColor = getCssVar('--text') || '#fafafa'
  const textMuted = getCssVar('--text-muted') || '#71717a'

  const cx = width / 2
  const cy = (height - legendHeight) / 2
  const maxAU = 1.8
  const scale = Math.min(width, height - legendHeight) / (2 * maxAU) * 0.85

  const g = s.append('g').attr('transform', `translate(${cx},${cy})`)

  // Glow filter for the sun
  const defs = s.append('defs')
  const filter = defs.append('filter').attr('id', 'glow')
  filter.append('feGaussianBlur').attr('stdDeviation', '4').attr('result', 'coloredBlur')
  const merge = filter.append('feMerge')
  merge.append('feMergeNode').attr('in', 'coloredBlur')
  merge.append('feMergeNode').attr('in', 'SourceGraphic')

  // Earth orbit (1 AU)
  g.append('circle')
    .attr('r', 1 * scale)
    .attr('fill', 'none')
    .attr('stroke', accentBlue)
    .attr('stroke-width', 1.8)
    .attr('stroke-dasharray', '6,4')
    .attr('opacity', 0.7)

  // Mars orbit (~1.524 AU)
  g.append('circle')
    .attr('r', 1.524 * scale)
    .attr('fill', 'none')
    .attr('stroke', '#ef4444')
    .attr('stroke-width', 1.8)
    .attr('stroke-dasharray', '6,4')
    .attr('opacity', 0.7)

  // Roadster orbit (ellipse) — derive semi-major axis from apoapsis/periapsis
  // because the API value can be unreliable
  const sma = (props.apoapsis + props.periapsis) / 2
  const a = sma * scale
  const c = ((props.apoapsis - props.periapsis) / 2) * scale
  const b = Math.sqrt(a * a - c * c)

  const roadsterOrbitColor = '#e67e22'
  g.append('ellipse')
    .attr('cx', -c)
    .attr('rx', a)
    .attr('ry', b)
    .attr('fill', 'none')
    .attr('stroke', roadsterOrbitColor)
    .attr('stroke-width', 3)
    .attr('opacity', 1)

  // Sun
  g.append('circle')
    .attr('r', 10)
    .attr('fill', '#fbbf24')
    .attr('filter', 'url(#glow)')

  // Sun label
  g.append('text')
    .attr('x', 0)
    .attr('y', -16)
    .attr('text-anchor', 'middle')
    .text('Sun')
    .attr('fill', '#fbbf24')
    .attr('font-size', '0.8rem')
    .attr('font-weight', '600')
    .attr('font-family', 'var(--font-mono)')

  // Earth dot on orbit
  const earthAngle = Math.PI * 0.7
  const earthX = 1 * scale * Math.cos(earthAngle)
  const earthY = 1 * scale * Math.sin(earthAngle)
  g.append('circle')
    .attr('cx', earthX)
    .attr('cy', earthY)
    .attr('r', 7)
    .attr('fill', accentBlue)

  g.append('text')
    .attr('x', earthX + 12)
    .attr('y', earthY - 10)
    .text('Earth')
    .attr('fill', accentBlue)
    .attr('font-size', '0.82rem')
    .attr('font-weight', '600')
    .attr('font-family', 'var(--font-mono)')

  // Mars dot on orbit
  const marsAngle = Math.PI * 1.8
  const marsX = 1.524 * scale * Math.cos(marsAngle)
  const marsY = 1.524 * scale * Math.sin(marsAngle)
  g.append('circle')
    .attr('cx', marsX)
    .attr('cy', marsY)
    .attr('r', 6)
    .attr('fill', '#ef4444')

  g.append('text')
    .attr('x', marsX + 12)
    .attr('y', marsY - 10)
    .text('Mars')
    .attr('fill', '#ef4444')
    .attr('font-size', '0.82rem')
    .attr('font-weight', '600')
    .attr('font-family', 'var(--font-mono)')

  // Roadster animated dot
  let roadsterAngle = 0
  const roadsterDot = g.append('circle')
    .attr('r', 6)
    .attr('fill', roadsterOrbitColor)
    .attr('stroke', textColor)
    .attr('stroke-width', 2)

  const roadsterLabel = g.append('text')
    .text('Roadster')
    .attr('fill', roadsterOrbitColor)
    .attr('font-size', '0.8rem')
    .attr('font-weight', '600')
    .attr('font-family', 'var(--font-mono)')

  function animateRoadster() {
    roadsterAngle += 0.003
    const x = -c + a * Math.cos(roadsterAngle)
    const y = b * Math.sin(roadsterAngle)
    roadsterDot.attr('cx', x).attr('cy', y)
    roadsterLabel.attr('x', x + 10).attr('y', y - 10)
    animId = requestAnimationFrame(animateRoadster)
  }
  animateRoadster()

  // Legend at the bottom
  const legendY = height - 14
  const legendItems = [
    { label: 'Earth orbit', color: accentBlue, dash: true },
    { label: 'Mars orbit', color: '#ef4444', dash: true },
    { label: 'Roadster orbit', color: roadsterOrbitColor, dash: false },
  ]

  const legendG = s.append('g').attr('transform', `translate(${cx}, ${legendY})`)
  const itemWidth = 130
  const startX = -(legendItems.length * itemWidth) / 2

  legendItems.forEach((item, i) => {
    const x = startX + i * itemWidth
    legendG.append('line')
      .attr('x1', x)
      .attr('y1', 0)
      .attr('x2', x + 24)
      .attr('y2', 0)
      .attr('stroke', item.color)
      .attr('stroke-width', 2.2)
      .attr('stroke-dasharray', item.dash ? '5,3' : 'none')

    legendG.append('text')
      .attr('x', x + 30)
      .attr('y', 4)
      .text(item.label)
      .attr('fill', textMuted)
      .attr('font-size', '0.75rem')
      .attr('font-family', 'var(--font-mono)')
  })
}

onMounted(() => {
  nextTick(() => {
    draw()
    resizeObserver = new ResizeObserver(() => draw())
    if (container.value) resizeObserver.observe(container.value)
  })
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  resizeObserver?.disconnect()
})

watch(() => [props.apoapsis, props.periapsis, props.semiMajorAxis], () => draw())
watch(() => themeStore.theme, () => nextTick(() => draw()))
</script>

<style scoped>
.orbit-chart {
  position: relative;
  width: 100%;
}

.orbit-chart svg {
  display: block;
}
</style>
