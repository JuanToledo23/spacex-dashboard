<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Rocket success rates"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { RocketSummary } from '@/types'

const props = defineProps<{ data: RocketSummary[] }>()
const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
const themeStore = useThemeStore()
let observer: ResizeObserver | null = null

function addDotGrid(defs: d3.Selection<SVGDefsElement, unknown, null, undefined>, id: string): void {
  const pattern = defs.append('pattern').attr('id', id).attr('width', 16).attr('height', 16).attr('patternUnits', 'userSpaceOnUse')
  pattern.append('circle').attr('cx', 1).attr('cy', 1).attr('r', 0.5).attr('fill', getCssVar('--chart-dot'))
}

function render() {
  if (!props.data.length || !container.value) return

  const el = d3.select(svg.value)
  el.selectAll('*').remove()
  d3.select(container.value).selectAll('.chart-tooltip').remove()

  const accentBlue = getCssVar('--accent-blue')
  const textMuted = getCssVar('--text-muted')
  const textSecondary = getCssVar('--text-secondary')
  const chartTrack = getCssVar('--chart-track')

  const width = container.value.clientWidth
  const barH = 36
  const m = { top: 8, right: 52, bottom: 16, left: 120 }
  const height = m.top + m.bottom + props.data.length * barH

  el.attr('width', width).attr('height', height)

  const defs = el.append('defs')
  addDotGrid(defs, 'dots-rocket')

  const iW = width - m.left - m.right
  const g = el.append('g').attr('transform', `translate(${m.left},${m.top})`)

  g.append('rect').attr('width', iW).attr('height', props.data.length * barH).attr('fill', 'url(#dots-rocket)')

  const x = d3.scaleLinear().domain([0, 100]).range([0, iW])
  const y = d3.scaleBand().domain(props.data.map((d) => d.name)).range([0, props.data.length * barH]).padding(0.35)

  // Y labels
  g.append('g').call(d3.axisLeft(y)).selectAll('text').style('font-family', 'var(--font-display)').style('font-size', '12px').style('fill', textSecondary)
  g.selectAll('.tick line, .domain').remove()

  // Tracks
  g.selectAll('.track').data(props.data).enter().append('rect').attr('y', (d) => y(d.name)).attr('width', iW).attr('height', y.bandwidth()).attr('fill', chartTrack).attr('rx', 2)

  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  // Bars
  g.selectAll('.bar')
    .data(props.data).enter().append('rect')
    .attr('y', (d) => y(d.name)).attr('width', 0).attr('height', y.bandwidth())
    .attr('fill', (d) => (d.active ? accentBlue : textMuted))
    .attr('rx', 2)
    .on('mouseover', (event, d) => {
      const status = d.active ? 'Active' : 'Retired'
      tooltip.html(`<strong>${d.name}</strong><br/>Success: ${d.success_rate_pct}%<br/>Launches: ${d.launch_count}<br/>${status}`).style('opacity', 1).style('left', `${event.offsetX + 12}px`).style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', () => tooltip.style('opacity', 0))
    .transition().duration(600).delay((_, i) => i * 60)
    .attr('width', (d) => x(d.success_rate_pct))

  // Value labels
  g.selectAll('.val')
    .data(props.data).enter().append('text')
    .attr('x', (d) => x(d.success_rate_pct) + 6)
    .attr('y', (d) => y(d.name) + y.bandwidth() / 2 + 4)
    .text((d) => d.success_rate_pct + '%')
    .style('font-family', 'var(--font-mono)').style('font-size', '12px').style('font-weight', '500').style('fill', textSecondary)
    .style('opacity', 0).transition().duration(300).delay(600).style('opacity', 1)
}

onMounted(() => { render(); observer = new ResizeObserver(() => render()); if (container.value) observer.observe(container.value) })
onUnmounted(() => observer?.disconnect())
watch(() => props.data, render, { deep: true })
watch(() => themeStore.theme, render)
</script>
