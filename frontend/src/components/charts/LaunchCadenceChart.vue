<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Launch cadence area chart"
  >
    <svg ref="svg" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import { useThemeStore } from '@/stores/theme'
import { getCssVar } from '@/utils/chartColors'
import type { LaunchAggregate } from '@/types'

const props = defineProps<{ data: LaunchAggregate[] }>()
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
  const textMuted = getCssVar('--text-muted')
  const chartGrid = getCssVar('--chart-grid')
  const chartAxis = getCssVar('--chart-axis')

  const width = container.value.clientWidth
  const height = 260
  const m = { top: 16, right: 16, bottom: 36, left: 44 }

  el.attr('width', width).attr('height', height)

  const defs = el.append('defs')
  addDotGrid(defs, 'dots-cadence')

  const grad = defs.append('linearGradient').attr('id', 'area-grad').attr('x1', 0).attr('y1', 0).attr('x2', 0).attr('y2', 1)
  grad.append('stop').attr('offset', '0%').attr('stop-color', accent).attr('stop-opacity', 0.25)
  grad.append('stop').attr('offset', '100%').attr('stop-color', accent).attr('stop-opacity', 0.01)

  const iW = width - m.left - m.right
  const iH = height - m.top - m.bottom
  const g = el.append('g').attr('transform', `translate(${m.left},${m.top})`)

  g.append('rect').attr('width', iW).attr('height', iH).attr('fill', 'url(#dots-cadence)')

  const x = d3.scaleLinear().domain(d3.extent(props.data, (d) => d.year)).range([0, iW])
  const maxVal = d3.max(props.data, (d) => d.total) || 1
  const y = d3.scaleLinear().domain([0, maxVal]).nice().range([iH, 0])

  // Grid lines
  g.append('g').call(d3.axisLeft(y).ticks(5).tickSize(-iW).tickFormat('')).selectAll('line').attr('stroke', chartGrid)
  g.selectAll('.domain').remove()

  // Axes
  g.append('g').attr('transform', `translate(0,${iH})`).call(d3.axisBottom(x).ticks(8).tickFormat((d) => d)).selectAll('text').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
  g.append('g').call(d3.axisLeft(y).ticks(5)).selectAll('text').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
  g.selectAll('.domain').attr('stroke', chartAxis)
  g.selectAll('.tick line').attr('stroke', chartAxis)

  g.append('text').attr('transform', 'rotate(-90)').attr('x', -iH / 2).attr('y', -32).attr('text-anchor', 'middle').text('Launches').style('font-family', 'var(--font-mono)').style('font-size', '11px').style('fill', textMuted)

  // Area
  const area = d3.area().x((d) => x(d.year)).y0(iH).y1((d) => y(d.total)).curve(d3.curveMonotoneX)
  g.append('path').datum(props.data).attr('d', area).attr('fill', 'url(#area-grad)')

  // Line
  const line = d3.line().x((d) => x(d.year)).y((d) => y(d.total)).curve(d3.curveMonotoneX)
  g.append('path').datum(props.data).attr('d', line).attr('fill', 'none').attr('stroke', accent).attr('stroke-width', 1.5)

  // Crosshair markers
  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  g.selectAll('.marker')
    .data(props.data)
    .enter()
    .append('g')
    .attr('transform', (d) => `translate(${x(d.year)},${y(d.total)})`)
    .each(function () {
      const marker = d3.select(this)
      marker.append('line').attr('x1', -4).attr('x2', 4).attr('y1', 0).attr('y2', 0).attr('stroke', accent).attr('stroke-width', 1)
      marker.append('line').attr('x1', 0).attr('x2', 0).attr('y1', -4).attr('y2', 4).attr('stroke', accent).attr('stroke-width', 1)
    })
    .on('mouseover', (event, d) => {
      tooltip.html(`<strong>${d.year}</strong><br/>Total: ${d.total}<br/>Success: ${d.successes}<br/>Failed: ${d.failures}`).style('opacity', 1).style('left', `${event.offsetX + 12}px`).style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', () => tooltip.style('opacity', 0))
    .append('rect').attr('x', -8).attr('y', -8).attr('width', 16).attr('height', 16).attr('fill', 'transparent')
}

onMounted(() => { render(); observer = new ResizeObserver(() => render()); if (container.value) observer.observe(container.value) })
onUnmounted(() => observer?.disconnect())
watch(() => props.data, render, { deep: true })
watch(() => themeStore.theme, render)
</script>
