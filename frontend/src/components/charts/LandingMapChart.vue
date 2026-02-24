<template>
  <div
    ref="container"
    class="landing-map"
    role="img"
    aria-label="Landing zones world map"
  >
    <svg ref="svg" />
    <div
      v-if="tooltip.show"
      class="map-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <strong>{{ tooltip.region }}</strong>
      <span class="tt-count">{{ tooltip.padCount }} landing pad{{ tooltip.padCount > 1 ? 's' : '' }}</span>
      <div
        v-for="pad in tooltip.pads"
        :key="pad.name"
        class="tt-pad"
      >
        <span class="tt-pad-name">{{ pad.name }}</span>
        <span
          class="tt-pad-type"
          :class="pad.type.toLowerCase()"
        >{{ pad.type }}</span>
        <span class="tt-pad-stats">{{ pad.successes }}/{{ pad.attempts }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import { getCssVar } from '@/utils/chartColors'
import { useThemeStore } from '@/stores/theme'
import type { LandpadSummary } from '@/types'

interface TooltipPad {
  name: string
  type: string
  attempts: number
  successes: number
}

interface TooltipState {
  show: boolean
  x: number
  y: number
  region: string
  padCount: number
  pads: TooltipPad[]
}

const props = defineProps<{ landpads: LandpadSummary[] }>()
const themeStore = useThemeStore()

const container = ref<HTMLDivElement | null>(null)
const svg = ref<SVGSVGElement | null>(null)
const tooltip = ref<TooltipState>({ show: false, x: 0, y: 0, region: '', padCount: 0, pads: [] })

let resizeObserver: ResizeObserver | null = null
let svgSelection: d3.Selection<SVGSVGElement, unknown, null, undefined> | null = null

function isDarkTheme() {
  return document.documentElement.getAttribute('data-theme') !== 'light'
}

async function draw() {
  if (!svg.value || !container.value) return

  const el = container.value
  const width = el.clientWidth
  const height = Math.min(width * 0.55, 440)
  const dark = isDarkTheme()

  svgSelection = d3.select(svg.value)
  svgSelection.selectAll('*').remove()
  svgSelection.attr('width', width).attr('height', height)

  const accent = getCssVar('--accent') || '#d4915c'
  const accentBlue = getCssVar('--accent-blue') || '#5b8def'

  // High-contrast colors per theme
  const oceanFill = dark ? '#0c1017' : '#e8edf4'
  const landFill = dark ? '#1e2330' : '#cdd4de'
  const landStroke = dark ? '#2d3548' : '#a8b2c2'
  const borderStroke = dark ? '#2a3040' : '#b0b8c8'
  const graticuleStroke = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.06)'

  const projection = d3.geoNaturalEarth1()
    .fitSize([width, height], { type: 'Sphere' })

  const path = d3.geoPath(projection)

  let world
  try {
    const resp = await fetch('/data/world-110m.json')
    world = await resp.json()
  } catch {
    return
  }

  const countries = topojson.feature(world, world.objects.countries)

  // Zoom group
  const g = svgSelection.append('g')

  // Ocean background
  g.append('path')
    .datum({ type: 'Sphere' })
    .attr('d', path)
    .attr('fill', oceanFill)
    .attr('stroke', borderStroke)
    .attr('stroke-width', 1)

  // Graticule for visual reference
  const graticule = d3.geoGraticule()
  g.append('path')
    .datum(graticule())
    .attr('d', path)
    .attr('fill', 'none')
    .attr('stroke', graticuleStroke)
    .attr('stroke-width', 0.4)

  // Countries
  g.append('path')
    .datum(countries)
    .attr('d', path)
    .attr('fill', landFill)
    .attr('stroke', landStroke)
    .attr('stroke-width', 0.6)

  // Cluster pads by geographic proximity
  interface PadCluster {
    pads: LandpadSummary[]
    longitude: number
    latitude: number
    region: string
    isRTLS: boolean
  }

  function clusterPads(pads: LandpadSummary[], proj: d3.GeoProjection, threshold = 30): PadCluster[] {
    const clusters: PadCluster[] = []
    const used = new Set<number>()
    for (let i = 0; i < pads.length; i++) {
      if (used.has(i)) continue
      const pt = proj([pads[i].longitude, pads[i].latitude])
      if (!pt) continue
      const group = [pads[i]]
      used.add(i)
      for (let j = i + 1; j < pads.length; j++) {
        if (used.has(j)) continue
        const pt2 = proj([pads[j].longitude, pads[j].latitude])
        if (!pt2) continue
        if (Math.hypot(pt2[0] - pt[0], pt2[1] - pt[1]) < threshold) {
          group.push(pads[j])
          used.add(j)
        }
      }
      const avgLon = group.reduce((s, p) => s + p.longitude, 0) / group.length
      const avgLat = group.reduce((s, p) => s + p.latitude, 0) / group.length
      const region = group[0].locality || group[0].region || group[0].name
      const rtlsCount = group.filter((p) => p.type === 'RTLS').length
      clusters.push({ pads: group, longitude: avgLon, latitude: avgLat, region, isRTLS: rtlsCount > group.length / 2 })
    }
    return clusters
  }

  const clusters = clusterPads(props.landpads, projection)

  // Style tokens
  const markerStroke = dark ? '#ffffff' : '#18181b'
  const labelColor = dark ? 'rgba(255,255,255,0.75)' : 'rgba(0,0,0,0.65)'
  const badgeBg = dark ? '#ffffff' : '#18181b'
  const badgeText = dark ? '#09090b' : '#fafafa'
  const MARKER_R = 10

  // Cluster markers
  const clusterGroups = g.selectAll('g.cluster')
    .data(clusters)
    .join('g')
    .attr('class', 'cluster')
    .style('cursor', 'pointer')

  // Main circle per cluster
  clusterGroups.append('circle')
    .attr('cx', (d) => projection([d.longitude, d.latitude])?.[0] ?? -100)
    .attr('cy', (d) => projection([d.longitude, d.latitude])?.[1] ?? -100)
    .attr('r', MARKER_R)
    .attr('fill', (d) => d.isRTLS ? accent : accentBlue)
    .attr('fill-opacity', 0.9)
    .attr('stroke', markerStroke)
    .attr('stroke-width', 1.5)

  // Count badge (top-right)
  clusterGroups.append('circle')
    .attr('cx', (d) => (projection([d.longitude, d.latitude])?.[0] ?? -100) + MARKER_R * 0.7)
    .attr('cy', (d) => (projection([d.longitude, d.latitude])?.[1] ?? -100) - MARKER_R * 0.7)
    .attr('r', 7)
    .attr('fill', badgeBg)
    .attr('stroke', 'none')

  clusterGroups.append('text')
    .attr('x', (d) => (projection([d.longitude, d.latitude])?.[0] ?? -100) + MARKER_R * 0.7)
    .attr('y', (d) => (projection([d.longitude, d.latitude])?.[1] ?? -100) - MARKER_R * 0.7 + 3.5)
    .attr('text-anchor', 'middle')
    .attr('font-size', '8px')
    .attr('font-weight', '700')
    .attr('font-family', 'IBM Plex Mono, Consolas, monospace')
    .attr('fill', badgeText)
    .attr('pointer-events', 'none')
    .text((d) => d.pads.length)

  // Region label below
  clusterGroups.append('text')
    .attr('x', (d) => projection([d.longitude, d.latitude])?.[0] ?? -100)
    .attr('y', (d) => (projection([d.longitude, d.latitude])?.[1] ?? -100) + MARKER_R + 14)
    .attr('text-anchor', 'middle')
    .attr('font-size', '9px')
    .attr('font-weight', '600')
    .attr('font-family', 'IBM Plex Mono, Consolas, monospace')
    .attr('fill', labelColor)
    .attr('pointer-events', 'none')
    .text((d) => d.region)

  // Tooltip on hover
  clusterGroups
    .on('mouseenter', (event, d) => {
      d3.select(event.currentTarget).select('circle').attr('fill-opacity', 1).attr('stroke-width', 2.5)
      const rect = container.value.getBoundingClientRect()
      tooltip.value = {
        show: true,
        x: event.clientX - rect.left + 14,
        y: event.clientY - rect.top - 10,
        region: d.region,
        padCount: d.pads.length,
        pads: d.pads.map((p) => ({
          name: p.name,
          type: p.type,
          attempts: p.landing_attempts,
          successes: p.landing_successes,
        })),
      }
    })
    .on('mouseleave', (event) => {
      d3.select(event.currentTarget).select('circle').attr('fill-opacity', 0.9).attr('stroke-width', 1.5)
      tooltip.value.show = false
    })

}

onMounted(() => {
  nextTick(() => {
    draw()
    resizeObserver = new ResizeObserver(() => draw())
    if (container.value) resizeObserver.observe(container.value)
  })
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})

watch(() => props.landpads, () => draw(), { deep: true })
watch(() => themeStore.theme, () => nextTick(() => draw()))
</script>

<style scoped>
.landing-map {
  position: relative;
  width: 100%;
}

.landing-map svg {
  display: block;
}

.map-tooltip {
  position: absolute;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  padding: 10px 14px;
  pointer-events: none;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.82rem;
  color: var(--text);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  white-space: nowrap;
}

.map-tooltip strong {
  font-family: var(--font-display);
  font-size: 0.9rem;
}

.tt-count {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.tt-pad {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
  border-top: 1px solid var(--border);
}

.tt-pad-name {
  font-weight: 600;
  color: var(--text);
  flex: 1;
}

.tt-pad-type {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 1px 5px;
  border-radius: 3px;
}

.tt-pad-type.rtls {
  background: color-mix(in srgb, var(--accent) 20%, transparent);
  color: var(--accent);
}

.tt-pad-type.asds {
  background: color-mix(in srgb, var(--accent-blue) 20%, transparent);
  color: var(--accent-blue);
}

.tt-pad-stats {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
}
</style>
