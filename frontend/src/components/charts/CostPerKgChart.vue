<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Cost per kilogram to LEO by vehicle"
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
  const items = props.data.filter((d) => d.cost_per_kg_leo)
  if (!items.length || !container.value) return

  const el = d3.select(svg.value)
  el.selectAll('*').remove()

  const textColor = getCssVar('--text')
  const textMuted = getCssVar('--text-muted')
  const accent = getCssVar('--accent')
  const accentBlue = getCssVar('--accent-blue')
  const trackColor = getCssVar('--chart-track')

  const width = container.value.clientWidth
  const barHeight = 44
  const margin = { top: 8, right: 80, bottom: 8, left: 110 }
  const innerW = width - margin.left - margin.right
  const innerH = items.length * barHeight
  const height = innerH + margin.top + margin.bottom

  // Sort most expensive first
  items.sort((a, b) => b.cost_per_kg_leo - a.cost_per_kg_leo)

  el.attr('width', width).attr('height', height)

  const g = el.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleLog().domain([1, d3.max(items, (d) => d.cost_per_kg_leo) * 1.3]).range([0, innerW])
  const y = d3.scaleBand().domain(items.map((d) => d.rocket_name)).range([0, innerH]).padding(0.35)

  // Track bars
  g.selectAll('.track')
    .data(items)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d) => y(d.rocket_name))
    .attr('width', innerW)
    .attr('height', y.bandwidth())
    .attr('fill', trackColor)
    .attr('rx', 3)

  // Value bars
  g.selectAll('.bar')
    .data(items)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d) => y(d.rocket_name))
    .attr('width', 0)
    .attr('height', y.bandwidth())
    .attr('fill', (d, i) => (i === items.length - 1 ? accent : accentBlue))
    .attr('rx', 3)
    .style('opacity', 0.8)
    .transition()
    .duration(700)
    .attr('width', (d) => x(d.cost_per_kg_leo))

  // Labels left (rocket names)
  g.selectAll('.label')
    .data(items)
    .enter()
    .append('text')
    .attr('x', -12)
    .attr('y', (d) => y(d.rocket_name) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .text((d) => d.rocket_name)
    .style('font-family', 'var(--font-display)')
    .style('font-size', '0.88rem')
    .style('font-weight', '600')
    .style('fill', textColor)

  // Labels right (values)
  g.selectAll('.value')
    .data(items)
    .enter()
    .append('text')
    .attr('x', (d) => x(d.cost_per_kg_leo) + 8)
    .attr('y', (d) => y(d.rocket_name) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .text((d) => '$' + d.cost_per_kg_leo.toLocaleString() + '/kg')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '0.78rem')
    .style('font-weight', '600')
    .style('fill', textMuted)
    .style('opacity', 0)
    .transition()
    .delay(700)
    .style('opacity', 1)
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
