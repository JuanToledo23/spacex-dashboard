import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SpaceBackground from '@/components/layout/SpaceBackground.vue'

function mockCanvasContext() {
  return {
    clearRect: () => {},
    fillRect: () => {},
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    globalAlpha: 1,
    beginPath: () => {},
    arc: () => {},
    fill: () => {},
    stroke: () => {},
    moveTo: () => {},
    lineTo: () => {},
    save: () => {},
    restore: () => {},
    scale: () => {},
    setTransform: () => {},
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createRadialGradient: () => ({ addColorStop: () => {} }),
  }
}

describe('SpaceBackground', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    HTMLCanvasElement.prototype.getContext = () => mockCanvasContext() as any
  })

  it('renders canvas element', () => {
    const wrapper = mount(SpaceBackground)
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('has space-bg class', () => {
    const wrapper = mount(SpaceBackground)
    expect(wrapper.find('.space-bg').exists()).toBe(true)
  })

  it('canvas is decorative (aria-hidden)', () => {
    const wrapper = mount(SpaceBackground)
    const canvas = wrapper.find('canvas')
    expect(canvas.attributes('aria-hidden')).toBe('true')
  })
})
