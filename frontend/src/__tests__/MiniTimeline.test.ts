import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MiniTimeline from '@/components/common/MiniTimeline.vue'

const items = [
  {
    id: 'l1',
    name: 'Starlink 6-1',
    date_utc: '2023-07-01T00:00:00Z',
    success: true,
    upcoming: false,
    rocket_name: 'Falcon 9',
    patch_small: 'https://example.com/patch.png',
    webcast: 'https://youtube.com/watch?v=abc',
  },
  {
    id: 'l2',
    name: 'CRS-27',
    date_utc: '2023-03-15T00:00:00Z',
    success: false,
    upcoming: false,
    rocket_name: 'Falcon 9',
  },
  {
    id: 'l3',
    name: 'Crew-8',
    date_utc: '2024-01-01T00:00:00Z',
    success: null,
    upcoming: true,
  },
] as any

describe('MiniTimeline', () => {
  it('renders all items', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const tlItems = wrapper.findAll('.tl-item')
    expect(tlItems).toHaveLength(3)
  })

  it('shows mission names', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const names = wrapper.findAll('.tl-name')
    expect(names[0].text()).toBe('Starlink 6-1')
    expect(names[1].text()).toBe('CRS-27')
  })

  it('shows success/fail/pending markers', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const markers = wrapper.findAll('.tl-marker')
    expect(markers[0].classes()).toContain('ok')
    expect(markers[1].classes()).toContain('err')
    expect(markers[2].classes()).toContain('pending')
  })

  it('shows patch image when available', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const img = wrapper.find('.tl-patch-img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/patch.png')
    expect(img.attributes('alt')).toBe('Starlink 6-1 mission patch')
  })

  it('shows fallback SVG when no patch', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const svgs = wrapper.findAll('.tl-patch-fallback')
    expect(svgs.length).toBeGreaterThanOrEqual(1)
  })

  it('shows rocket name', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const rocket = wrapper.find('.tl-rocket')
    expect(rocket.text()).toBe('Falcon 9')
  })

  it('shows webcast link', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const webcast = wrapper.find('.tl-webcast')
    expect(webcast.exists()).toBe(true)
    expect(webcast.attributes('href')).toBe('https://youtube.com/watch?v=abc')
  })

  it('shows OK/FAIL result labels', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const results = wrapper.findAll('.tl-result')
    expect(results[0].text()).toBe('OK')
    expect(results[1].text()).toBe('FAIL')
    expect(results[2].text()).toBe('—')
  })

  it('shows connectors between items except last', () => {
    const wrapper = mount(MiniTimeline, { props: { items } })
    const connectors = wrapper.findAll('.tl-connector')
    expect(connectors).toHaveLength(2)
  })
})
