<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Booster reuse leaderboard"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { CoreSummary } from '@/types'

const props = defineProps<{ data: CoreSummary[] }>()
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

  const accent = getCssVar('--accent')
  const textSecondary = getCssVar('--text-secondary')
  const chartTrack = getCssVar('--chart-track')

  const top = props.data.slice(0, 10)

  const width = container.value.clientWidth
  const barH = 30
  const m = { top: 4, right: 44, bottom: 8, left: 72 }
  const height = m.top + m.bottom + top.length * barH

  el.attr('width', width).attr('height', height)

  const defs = el.append('defs')
  addDotGrid(defs, 'dots-core')

  const iW = width - m.left - m.right
  const g = el.append('g').attr('transform', `translate(${m.left},${m.top})`)

  g.append('rect').attr('width', iW).attr('height', top.length * barH).attr('fill', 'url(#dots-core)')

  const maxVal = d3.max(top, (d) => d.reuse_count) || 1
  const x = d3.scaleLinear().domain([0, maxVal]).nice().range([0, iW])
  const y = d3.scaleBand().domain(top.map((d) => d.serial)).range([0, top.length * barH]).padding(0.35)

  // Y labels — show serial with flight count for clarity
  g.append('g').call(d3.axisLeft(y).tickFormat((serial) => {
    const item = top.find((d) => d.serial === serial)
    return item ? `${serial}` : serial
  })).selectAll('text').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textSecondary)
  g.selectAll('.tick line, .domain').remove()

  g.append('text').attr('x', iW / 2).attr('y', top.length * barH + 4).attr('dy', '1em').attr('text-anchor', 'middle').text('Flights').style('font-family', 'var(--font-mono)').style('font-size', '11px').style('fill', textSecondary)

  // Track
  g.selectAll('.track').data(top).enter().append('rect').attr('y', (d) => y(d.serial)).attr('width', iW).attr('height', y.bandwidth()).attr('fill', chartTrack).attr('rx', 2)

  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  // Bars
  g.selectAll('.bar')
    .data(top)
    .enter()
    .append('rect')
    .attr('y', (d) => y(d.serial))
    .attr('width', 0)
    .attr('height', y.bandwidth())
    .attr('fill', accent)
    .attr('rx', 2)
    .on('mouseover', (event, d) => {
      tooltip.html(`<strong>${d.serial}</strong><br/>Flights: ${d.reuse_count + 1}<br/>Landings: ${d.total_landings}<br/>Status: ${d.status}`).style('opacity', 1).style('left', `${event.offsetX + 12}px`).style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', () => tooltip.style('opacity', 0))
    .transition()
    .duration(500)
    .delay((_, i) => i * 40)
    .attr('width', (d) => x(d.reuse_count))

  // Count labels
  g.selectAll('.val')
    .data(top)
    .enter()
    .append('text')
    .attr('x', (d) => x(d.reuse_count) + 6)
    .attr('y', (d) => y(d.serial) + y.bandwidth() / 2 + 4)
    .text((d) => d.reuse_count + 'x')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '12px')
    .style('font-weight', '500')
    .style('fill', accent)
    .style('opacity', 0)
    .transition().duration(200).delay(500)
    .style('opacity', 1)
}

onMounted(() => { render(); observer = new ResizeObserver(() => render()); if (container.value) observer.observe(container.value) })
onUnmounted(() => observer?.disconnect())
watch(() => props.data, render, { deep: true })
watch(() => themeStore.theme, render)
</script>
