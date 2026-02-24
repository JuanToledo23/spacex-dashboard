<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Annual estimated launch spend"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { AnnualSpend } from '@/types'

const props = withDefaults(defineProps<{
  data: AnnualSpend[]
  height?: number
}>(), { height: 280 })
const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
const themeStore = useThemeStore()
let observer: ResizeObserver | null = null

function render() {
  if (!props.data.length || !container.value) return

  const el = d3.select(svg.value)
  el.selectAll('*').remove()
  d3.select(container.value).selectAll('.chart-tooltip').remove()

  const textMuted = getCssVar('--text-muted')
  const accent = getCssVar('--accent')
  const gridColor = getCssVar('--chart-grid')

  const width = container.value.clientWidth
  const height = props.height
  const margin = { top: 16, right: 16, bottom: 32, left: 60 }
  const innerW = width - margin.left - margin.right
  const innerH = height - margin.top - margin.bottom

  el.attr('width', width).attr('height', height)
  const g = el.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleLinear().domain(d3.extent(props.data, (d) => d.year)).range([0, innerW])
  const y = d3.scaleLinear().domain([0, d3.max(props.data, (d) => d.total_spend) * 1.1]).range([innerH, 0])

  // Grid
  g.selectAll('.grid')
    .data(y.ticks(5))
    .enter()
    .append('line')
    .attr('x1', 0)
    .attr('x2', innerW)
    .attr('y1', (d) => y(d))
    .attr('y2', (d) => y(d))
    .attr('stroke', gridColor)

  // Area
  const area = d3.area()
    .x((d) => x(d.year))
    .y0(innerH)
    .y1((d) => y(d.total_spend))
    .curve(d3.curveMonotoneX)

  g.append('path')
    .datum(props.data)
    .attr('d', area)
    .attr('fill', accent)
    .style('opacity', 0.12)

  // Line
  const line = d3.line()
    .x((d) => x(d.year))
    .y((d) => y(d.total_spend))
    .curve(d3.curveMonotoneX)

  g.append('path')
    .datum(props.data)
    .attr('d', line)
    .attr('fill', 'none')
    .attr('stroke', accent)
    .attr('stroke-width', 2)
    .style('opacity', 0.9)

  // Dots
  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  g.selectAll('.dot')
    .data(props.data)
    .enter()
    .append('circle')
    .attr('cx', (d) => x(d.year))
    .attr('cy', (d) => y(d.total_spend))
    .attr('r', 3.5)
    .attr('fill', accent)
    .style('cursor', 'pointer')
    .on('mouseover', function (event, d) {
      d3.select(this).attr('r', 6)
      tooltip
        .html(`<strong>${d.year}</strong><br/>$${(d.total_spend / 1e6).toFixed(0)}M · ${d.launches} launches`)
        .style('opacity', 1)
        .style('left', `${event.offsetX + 12}px`)
        .style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', function () {
      d3.select(this).attr('r', 3.5)
      tooltip.style('opacity', 0)
    })

  // Axes
  g.append('g')
    .attr('transform', `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(8).tickFormat(d3.format('d')))
    .selectAll('text')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '11px')
    .style('fill', textMuted)

  g.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat((d) => '$' + (d / 1e6).toFixed(0) + 'M'))
    .selectAll('text')
    .style('font-family', 'var(--font-mono)')
    .style('font-size', '11px')
    .style('fill', textMuted)

  g.selectAll('.domain').attr('stroke', gridColor)
  g.selectAll('.tick line').attr('stroke', gridColor)
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
