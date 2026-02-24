<template>
  <div
    ref="container"
    class="fuel-breakdown"
    role="img"
    aria-label="Propellant fuel breakdown chart"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { getCssVar } from '@/utils/chartColors'
import type { FuelBreakdown } from '@/types'

const props = withDefaults(defineProps<{
  data: FuelBreakdown[]
  height?: number
}>(), { height: 260 })

const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

function draw() {
  if (!svg.value || !container.value || !props.data.length) return

  const el = container.value
  const width = el.clientWidth
  const height = props.height

  const s = d3.select(svg.value)
  s.selectAll('*').remove()
  s.attr('width', width).attr('height', height)

  const accent = getCssVar('--accent') || '#d4915c'
  const accentBlue = getCssVar('--accent-blue') || '#5b8def'

  const colors = [accent, accentBlue, '#22c55e', '#ef4444']

  const radius = Math.min(width, height) / 2 - 20
  const cx = width / 2
  const cy = height / 2

  const g = s.append('g').attr('transform', `translate(${cx},${cy})`)

  const pie = d3.pie()
    .value(d => d.fuel_tonnes)
    .sort(null)
    .padAngle(0.03)

  const arc = d3.arc()
    .innerRadius(radius * 0.55)
    .outerRadius(radius)

  const arcs = g.selectAll('.arc')
    .data(pie(props.data))
    .join('g')
    .attr('class', 'arc')

  arcs.append('path')
    .attr('d', arc)
    .attr('fill', (d, i) => colors[i % colors.length])
    .attr('opacity', 0.85)

  // Labels
  const labelArc = d3.arc()
    .innerRadius(radius * 0.78)
    .outerRadius(radius * 0.78)

  arcs.each(function (d, _i) {
    const [lx, ly] = labelArc.centroid(d)
    const item = d.data

    d3.select(this).append('text')
      .attr('x', lx)
      .attr('y', ly - 6)
      .attr('text-anchor', 'middle')
      .text(item.fuel_type.split(' ')[0])
      .attr('fill', '#fff')
      .attr('font-size', '0.72rem')
      .attr('font-weight', '600')
      .attr('font-family', 'var(--font-mono)')
      .style('text-shadow', '0 1px 3px rgba(0,0,0,0.5)')

    d3.select(this).append('text')
      .attr('x', lx)
      .attr('y', ly + 10)
      .attr('text-anchor', 'middle')
      .text(`${item.percentage}%`)
      .attr('fill', 'rgba(255,255,255,0.85)')
      .attr('font-size', '0.68rem')
      .attr('font-family', 'var(--font-mono)')
      .style('text-shadow', '0 1px 3px rgba(0,0,0,0.5)')
  })

  // Center text
  g.append('text')
    .attr('text-anchor', 'middle')
    .attr('y', -4)
    .text(`${Math.round(props.data.reduce((s, d) => s + d.fuel_tonnes, 0)).toLocaleString()}`)
    .attr('fill', '#fff')
    .attr('font-size', '1.3rem')
    .attr('font-weight', '700')
    .attr('font-family', 'var(--font-display)')
    .style('text-shadow', '0 1px 4px rgba(0,0,0,0.6)')

  g.append('text')
    .attr('text-anchor', 'middle')
    .attr('y', 14)
    .text('tonnes total')
    .attr('fill', 'rgba(255,255,255,0.7)')
    .attr('font-size', '0.65rem')
    .attr('font-family', 'var(--font-mono)')
    .style('text-shadow', '0 1px 3px rgba(0,0,0,0.5)')
}

onMounted(() => {
  nextTick(() => {
    draw()
    resizeObserver = new ResizeObserver(() => draw())
    if (container.value) resizeObserver.observe(container.value)
  })
})

onUnmounted(() => { resizeObserver?.disconnect() })

watch(() => props.data, () => draw(), { deep: true })
</script>

<style scoped>
.fuel-breakdown { position: relative; width: 100%; }
.fuel-breakdown svg { display: block; }
</style>
