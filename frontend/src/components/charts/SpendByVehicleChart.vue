<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Spend distribution by vehicle"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { CostByVehicle } from '@/types'

const props = defineProps<{ data: CostByVehicle[] }>()
const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
const themeStore = useThemeStore()
let observer: ResizeObserver | null = null

function render() {
  const items = props.data.filter((d) => d.total_spend > 0)
  if (!items.length || !container.value) return

  const el = d3.select(svg.value)
  el.selectAll('*').remove()
  d3.select(container.value).selectAll('.chart-tooltip').remove()

  const textColor = getCssVar('--text')
  const textMuted = getCssVar('--text-muted')
  const colors = [
    getCssVar('--accent'),
    getCssVar('--accent-blue'),
    getCssVar('--accent-cyan'),
    getCssVar('--text-secondary'),
  ]

  const width = container.value.clientWidth
  const height = 240
  const radius = Math.min(width, height) / 2 - 24

  el.attr('width', width).attr('height', height)
  const g = el.append('g').attr('transform', `translate(${width / 2},${height / 2})`)

  const color = d3.scaleOrdinal().domain(items.map((d) => d.rocket_name)).range(colors)
  const pie = d3.pie().value((d) => d.total_spend).sort(null).padAngle(0.02)
  const arc = d3.arc().innerRadius(radius * 0.56).outerRadius(radius)
  const arcHover = d3.arc().innerRadius(radius * 0.56).outerRadius(radius + 4)

  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)
  const total = d3.sum(items, (d) => d.total_spend)

  const arcs = g.selectAll('.arc').data(pie(items)).enter().append('g')

  arcs
    .append('path')
    .attr('d', arc)
    .attr('fill', (d) => color(d.data.rocket_name))
    .style('opacity', 0.8)
    .on('mouseover', function (event, d) {
      d3.select(this).transition().duration(120).attr('d', arcHover).style('opacity', 1)
      const pct = ((d.data.total_spend / total) * 100).toFixed(1)
      tooltip
        .html(`<strong>${d.data.rocket_name}</strong><br/>$${(d.data.total_spend / 1e9).toFixed(2)}B (${pct}%)`)
        .style('opacity', 1)
        .style('left', `${event.offsetX + 12}px`)
        .style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', function () {
      d3.select(this).transition().duration(120).attr('d', arc).style('opacity', 0.8)
      tooltip.style('opacity', 0)
    })

  // Center text
  g.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '-0.15em')
    .text('$' + (total / 1e9).toFixed(1) + 'B')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '1.3rem')
    .style('font-weight', '600')
    .style('fill', textColor)

  g.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '1.2em')
    .text('TOTAL SPEND')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '0.65rem')
    .style('letter-spacing', '0.12em')
    .style('fill', textMuted)

  // Legend
  const lg = el.append('g').attr('transform', `translate(${width - 130}, 14)`)
  items.forEach((d, i) => {
    const row = lg.append('g').attr('transform', `translate(0, ${i * 20})`)
    row.append('rect').attr('width', 8).attr('height', 8).attr('rx', 1).attr('fill', color(d.rocket_name))
    row
      .append('text')
      .attr('x', 14)
      .attr('y', 7)
      .text(`${d.rocket_name}`)
      .style('font-family', 'var(--font-mono)')
      .style('font-size', '12px')
      .style('fill', textMuted)
  })
}

onMounted(() => {
  render()
  observer = new ResizeObserver(() => render())
  observer.observe(container.value)
})
onUnmounted(() => observer?.disconnect())
watch(() => props.data, render, { deep: true })
watch(() => themeStore.theme, render)
</script>
