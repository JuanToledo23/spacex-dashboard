<template>
  <div
    ref="container"
    class="chart-container"
    role="img"
    aria-label="Launches by year grouped bar chart"
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

const props = withDefaults(defineProps<{
  data: LaunchAggregate[]
  height?: number
}>(), { height: 300 })
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

  const successColor = getCssVar('--success')
  const errorColor = getCssVar('--error')
  const textMuted = getCssVar('--text-muted')
  const chartGrid = getCssVar('--chart-grid')
  const chartAxis = getCssVar('--chart-axis')

  const width = container.value.clientWidth
  const height = props.height
  const m = { top: 20, right: 16, bottom: 48, left: 44 }

  el.attr('width', width).attr('height', height)

  const defs = el.append('defs')
  addDotGrid(defs, 'dots-year')

  const iW = width - m.left - m.right
  const iH = height - m.top - m.bottom
  const g = el.append('g').attr('transform', `translate(${m.left},${m.top})`)

  g.append('rect').attr('width', iW).attr('height', iH).attr('fill', 'url(#dots-year)')

  const x = d3.scaleBand().domain(props.data.map((d) => d.year)).range([0, iW]).padding(0.3)
  const maxVal = d3.max(props.data, (d) => d.total) || 1
  const y = d3.scaleLinear().domain([0, maxVal]).nice().range([iH, 0])

  // Grid
  g.append('g').call(d3.axisLeft(y).ticks(5).tickSize(-iW).tickFormat('')).selectAll('line').attr('stroke', chartGrid)
  g.selectAll('.domain').remove()

  // Axes
  g.append('g').attr('transform', `translate(0,${iH})`).call(d3.axisBottom(x).tickFormat((d) => d)).selectAll('text').attr('transform', 'rotate(-45)').style('text-anchor', 'end').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
  g.append('g').call(d3.axisLeft(y).ticks(5)).selectAll('text').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
  g.selectAll('.domain').attr('stroke', chartAxis)
  g.selectAll('.tick line').attr('stroke', chartAxis)

  g.append('text').attr('transform', 'rotate(-90)').attr('x', -iH / 2).attr('y', -32).attr('text-anchor', 'middle').text('Launches').style('font-family', 'var(--font-mono)').style('font-size', '11px').style('fill', textMuted)

  const tooltip = d3.select(container.value).append('div').attr('class', 'chart-tooltip').style('opacity', 0)

  const barW = x.bandwidth() / 2 - 1

  // Success bars
  g.selectAll('.bar-s')
    .data(props.data).enter().append('rect')
    .attr('x', (d) => x(d.year)).attr('y', iH).attr('width', barW).attr('height', 0)
    .attr('fill', successColor).attr('rx', 2)
    .on('mouseover', (event, d) => {
      tooltip.html(`<strong>${d.year}</strong><br/>Success: ${d.successes}<br/>Failed: ${d.failures}`).style('opacity', 1).style('left', `${event.offsetX + 12}px`).style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', () => tooltip.style('opacity', 0))
    .transition().duration(500).delay((_, i) => i * 25)
    .attr('y', (d) => y(d.successes)).attr('height', (d) => iH - y(d.successes))

  // Failure bars
  g.selectAll('.bar-f')
    .data(props.data).enter().append('rect')
    .attr('x', (d) => x(d.year) + barW + 2).attr('y', iH).attr('width', barW).attr('height', 0)
    .attr('fill', errorColor).attr('rx', 2)
    .on('mouseover', (event, d) => {
      tooltip.html(`<strong>${d.year}</strong><br/>Failed: ${d.failures}`).style('opacity', 1).style('left', `${event.offsetX + 12}px`).style('top', `${event.offsetY - 12}px`)
    })
    .on('mouseout', () => tooltip.style('opacity', 0))
    .transition().duration(500).delay((_, i) => i * 25)
    .attr('y', (d) => y(d.failures)).attr('height', (d) => iH - y(d.failures))

  // Legend
  const lg = el.append('g').attr('transform', `translate(${width - m.right - 130}, 6)`)
  lg.append('rect').attr('width', 8).attr('height', 8).attr('fill', successColor)
  lg.append('text').attr('x', 12).attr('y', 7).text('Success').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
  lg.append('rect').attr('x', 66).attr('width', 8).attr('height', 8).attr('fill', errorColor)
  lg.append('text').attr('x', 78).attr('y', 7).text('Failed').style('font-family', 'var(--font-mono)').style('font-size', '12px').style('fill', textMuted)
}

onMounted(() => { render(); observer = new ResizeObserver(() => render()); if (container.value) observer.observe(container.value) })
onUnmounted(() => observer?.disconnect())
watch(() => props.data, render, { deep: true })
watch(() => themeStore.theme, render)
</script>
