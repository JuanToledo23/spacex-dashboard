<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Total mass launched by orbit type"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { OrbitMass } from '@/types'

const props = defineProps<{ data: OrbitMass[] }>()
const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
const themeStore = useThemeStore()
let observer: ResizeObserver | null = null

const orbitNames: Record<string, string> = {
  LEO: 'Low Earth',
  GTO: 'Geo Transfer',
  SSO: 'Sun-Sync',
  MEO: 'Mid Earth',
  GEO: 'Geostationary',
  HEO: 'High Earth',
  ISS: 'Space Station',
  PO: 'Polar',
  ES: 'Earth-Sun',
  SO: 'Sub-Orbital',
}

function humanOrbit(code: string): string {
  return orbitNames[code] || code
}

function render() {
  if (!props.data.length || !container.value) return

  // Show top 8 orbits
  const items = props.data.slice(0, 8)

  const el = d3.select(svg.value)
  el.selectAll('*').remove()
  d3.select(container.value).selectAll('.chart-tooltip').remove()

  const textColor = getCssVar('--text')
  const textMuted = getCssVar('--text-muted')
  const accentBlue = getCssVar('--accent-blue')
  const accentCyan = getCssVar('--accent-cyan')
  const trackColor = getCssVar('--chart-track')

  const width = container.value.clientWidth
  const barHeight = 36

  const tempText = el.append('text')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '0.78rem')
    .style('font-weight', '600')
    .style('visibility', 'hidden')
  let maxLabelW = 60
  for (const d of items) {
    tempText.text(humanOrbit(d.orbit))
    const w = (tempText.node() as SVGTextElement).getComputedTextLength()
    if (w > maxLabelW) maxLabelW = w
  }
  tempText.remove()

  const rightMargin = width < 400 ? 70 : 90
  const margin = { top: 8, right: rightMargin, bottom: 8, left: Math.ceil(maxLabelW) + 16 }
  const innerW = width - margin.left - margin.right
  const innerH = items.length * barHeight
  const height = innerH + margin.top + margin.bottom

  el.attr('width', width).attr('height', height)
  const g = el.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const maxVal = d3.max(items, (d) => d.total_mass_kg)
  const x = d3.scaleLinear().domain([0, maxVal * 1.1]).range([0, innerW])
  const y = d3.scaleBand().domain(items.map((d) => d.orbit)).range([0, innerH]).padding(0.3)

  const colorScale = d3.scaleLinear().domain([0, items.length - 1]).range([accentCyan, accentBlue])

  // Track
  g.selectAll('.track')
    .data(items)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d) => y(d.orbit))
    .attr('width', innerW)
    .attr('height', y.bandwidth())
    .attr('fill', trackColor)
    .attr('rx', 3)

  // Tooltip
  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  // Bars
  g.selectAll('.bar')
    .data(items)
    .enter()
    .append('rect')
    .attr('x', 0)
    .attr('y', (d) => y(d.orbit))
    .attr('width', 0)
    .attr('height', y.bandwidth())
    .attr('fill', (d, i) => colorScale(i))
    .attr('rx', 3)
    .style('opacity', 0.75)
    .style('cursor', 'pointer')
    .on('mouseover', function (event, d) {
      d3.select(this).style('opacity', 1)
      tooltip
        .html(`<strong>${d.orbit}</strong><br/>${d.total_mass_kg.toLocaleString()} kg · ${d.payloads} payloads`)
        .style('opacity', 1)
        .style('left', `${event.offsetX + 12}px`)
        .style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', function () {
      d3.select(this).style('opacity', 0.75)
      tooltip.style('opacity', 0)
    })
    .transition()
    .duration(600)
    .attr('width', (d) => x(d.total_mass_kg))

  // Labels left
  g.selectAll('.label')
    .data(items)
    .enter()
    .append('text')
    .attr('x', -8)
    .attr('y', (d) => y(d.orbit) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .text((d) => humanOrbit(d.orbit))
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '0.78rem')
    .style('font-weight', '600')
    .style('fill', textColor)

  // Labels right
  g.selectAll('.value')
    .data(items)
    .enter()
    .append('text')
    .attr('x', (d) => x(d.total_mass_kg) + 8)
    .attr('y', (d) => y(d.orbit) + y.bandwidth() / 2)
    .attr('dy', '0.35em')
    .text((d) => {
      if (d.total_mass_kg >= 1000) return (d.total_mass_kg / 1000).toFixed(0) + ' tonnes'
      return d.total_mass_kg.toFixed(0) + ' kg'
    })
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '0.72rem')
    .style('fill', textMuted)
    .style('opacity', 0)
    .transition()
    .delay(600)
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
