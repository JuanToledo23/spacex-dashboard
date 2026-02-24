<template>
  <div
    ref="container"
    class="emissions-timeline"
    role="img"
    aria-label="Annual CO₂ emissions timeline"
  >
    <svg ref="svg" />
    <div
      v-show="tip.show"
      class="chart-tip"
      :style="{ left: tip.x + 'px', top: tip.y + 'px' }"
    >
      <strong class="tip-year">{{ tip.data.year }}</strong>
      <div class="tip-row">
        <span class="tip-label">CO&#x2082; emitted</span><span class="tip-val accent">{{ fmtNum(tip.data.co2_tonnes) }}t</span>
      </div>
      <div class="tip-row">
        <span class="tip-label">Fuel burned</span><span class="tip-val">{{ fmtNum(tip.data.fuel_burned_tonnes) }}t</span>
      </div>
      <div class="tip-row">
        <span class="tip-label">Launches</span><span class="tip-val">{{ tip.data.launches }}</span>
      </div>
      <div
        v-if="tip.data.reuse_savings_tonnes > 0"
        class="tip-row"
      >
        <span class="tip-label">Reuse saved</span><span class="tip-val green">{{ fmtNum(tip.data.reuse_savings_tonnes) }}t</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { getCssVar } from '@/utils/chartColors'
import type { AnnualEmissions } from '@/types'

interface TipData {
  year: number
  co2_tonnes: number
  fuel_burned_tonnes: number
  launches: number
  reuse_savings_tonnes: number
}

const props = withDefaults(defineProps<{
  data: AnnualEmissions[]
  height?: number
}>(), { height: 320 })

const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
let resizeObserver: ResizeObserver | null = null

const tip = ref<{ show: boolean; x: number; y: number; data: TipData }>({
  show: false, x: 0, y: 0,
  data: { year: 0, co2_tonnes: 0, fuel_burned_tonnes: 0, launches: 0, reuse_savings_tonnes: 0 },
})

function fmtNum(n: number | null | undefined): string {
  if (!n && n !== 0) return '0'
  return Math.round(n).toLocaleString()
}

function draw() {
  if (!svg.value || !container.value || !props.data.length) return

  const el = container.value
  const width = el.clientWidth
  const height = props.height

  const s = d3.select(svg.value)
  s.selectAll('*').remove()
  s.attr('width', width).attr('height', height)

  const accent = getCssVar('--accent') || '#d4915c'
  const success = getCssVar('--success') || '#22c55e'
  const textMuted = getCssVar('--text-muted') || '#71717a'
  const border = getCssVar('--border') || 'rgba(255,255,255,0.06)'

  const margin = { top: 20, right: 20, bottom: 36, left: 56 }
  const w = width - margin.left - margin.right
  const h = height - margin.top - margin.bottom

  const g = s.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleBand()
    .domain(props.data.map(d => d.year))
    .range([0, w])
    .padding(0.15)

  const maxCo2 = d3.max(props.data, d => d.co2_tonnes) || 1
  const y = d3.scaleLinear()
    .domain([0, maxCo2 * 1.15])
    .range([h, 0])

  // Grid lines
  const ticks = y.ticks(5)
  ticks.forEach(tick => {
    g.append('line')
      .attr('x1', 0).attr('x2', w)
      .attr('y1', y(tick)).attr('y2', y(tick))
      .attr('stroke', border)
      .attr('stroke-dasharray', '3,3')
  })

  // Bars for CO2
  g.selectAll('.bar-co2')
    .data(props.data)
    .join('rect')
    .attr('class', 'bar-co2')
    .attr('x', d => x(d.year))
    .attr('y', d => y(d.co2_tonnes))
    .attr('width', x.bandwidth())
    .attr('height', d => h - y(d.co2_tonnes))
    .attr('fill', accent)
    .attr('opacity', 0.75)
    .attr('rx', 2)
    .style('cursor', 'pointer')
    .on('mouseenter', function (event, d) {
      d3.select(this).attr('opacity', 1)
      const rect = el.getBoundingClientRect()
      const ex = event.clientX - rect.left
      const ey = event.clientY - rect.top
      tip.value = { show: true, x: ex + 14, y: ey - 10, data: d }
    })
    .on('mousemove', function (event) {
      const rect = el.getBoundingClientRect()
      tip.value.x = event.clientX - rect.left + 14
      tip.value.y = event.clientY - rect.top - 10
    })
    .on('mouseleave', function () {
      d3.select(this).attr('opacity', 0.75)
      tip.value.show = false
    })

  // Reuse savings line
  const lineGen = d3.line()
    .x(d => x(d.year) + x.bandwidth() / 2)
    .y(d => y(d.reuse_savings_tonnes))
    .curve(d3.curveMonotoneX)

  const dataWithSavings = props.data.filter(d => d.reuse_savings_tonnes > 0)
  if (dataWithSavings.length > 1) {
    g.append('path')
      .datum(dataWithSavings)
      .attr('d', lineGen)
      .attr('fill', 'none')
      .attr('stroke', success)
      .attr('stroke-width', 2.5)
      .attr('stroke-dasharray', '6,3')

    g.selectAll('.dot-savings')
      .data(dataWithSavings)
      .join('circle')
      .attr('cx', d => x(d.year) + x.bandwidth() / 2)
      .attr('cy', d => y(d.reuse_savings_tonnes))
      .attr('r', 3.5)
      .attr('fill', success)
  }

  // X axis
  const xAxis = g.append('g')
    .attr('transform', `translate(0,${h})`)
    .call(d3.axisBottom(x).tickSize(0))
  xAxis.select('.domain').remove()
  xAxis.selectAll('text')
    .attr('fill', textMuted)
    .attr('font-size', '0.7rem')
    .attr('font-family', 'var(--font-mono)')
    .attr('dy', '10')

  // Y axis
  const yAxis = g.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => d >= 1000 ? `${(d / 1000).toFixed(0)}k` : d))
  yAxis.select('.domain').remove()
  yAxis.selectAll('line').remove()
  yAxis.selectAll('text')
    .attr('fill', textMuted)
    .attr('font-size', '0.68rem')
    .attr('font-family', 'var(--font-mono)')

  // Y axis label
  g.append('text')
    .attr('x', -margin.left + 8)
    .attr('y', -8)
    .text('tonnes CO₂')
    .attr('fill', textMuted)
    .attr('font-size', '0.65rem')
    .attr('font-family', 'var(--font-mono)')

  // Legend
  const legendY = -6
  const legendX = w - 200

  g.append('rect')
    .attr('x', legendX).attr('y', legendY - 4)
    .attr('width', 12).attr('height', 12)
    .attr('fill', accent).attr('opacity', 0.75).attr('rx', 2)
  g.append('text')
    .attr('x', legendX + 17).attr('y', legendY + 5)
    .text('CO₂ Emitted')
    .attr('fill', textMuted).attr('font-size', '0.68rem')
    .attr('font-family', 'var(--font-mono)')

  g.append('line')
    .attr('x1', legendX + 105).attr('x2', legendX + 125)
    .attr('y1', legendY + 2).attr('y2', legendY + 2)
    .attr('stroke', success).attr('stroke-width', 2.5)
    .attr('stroke-dasharray', '5,3')
  g.append('text')
    .attr('x', legendX + 130).attr('y', legendY + 5)
    .text('Reuse Saved')
    .attr('fill', textMuted).attr('font-size', '0.68rem')
    .attr('font-family', 'var(--font-mono)')
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
.emissions-timeline { position: relative; width: 100%; }
.emissions-timeline svg { display: block; }

.chart-tip {
  position: absolute;
  pointer-events: none;
  z-index: 10;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  padding: 10px 14px;
  min-width: 170px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.tip-year {
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
  display: block;
  margin-bottom: 6px;
}

.tip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 2px 0;
}

.tip-label {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tip-val {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text);
}

.tip-val.accent { color: var(--accent); }
.tip-val.green { color: var(--success); }
</style>
