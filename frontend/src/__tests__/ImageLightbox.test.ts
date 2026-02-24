import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageLightbox from '@/components/common/ImageLightbox.vue'

const images = ['img1.jpg', 'img2.jpg', 'img3.jpg']

describe('ImageLightbox', () => {
  it('does not render when not visible', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: false },
    })
    expect(wrapper.find('.lightbox-overlay').exists()).toBe(false)
  })

  it('renders when visible', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true },
      attachTo: document.body,
    })
    const overlay = document.querySelector('.lightbox-overlay')
    expect(overlay).toBeTruthy()
    wrapper.unmount()
  })

  it('shows current image', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true, startIndex: 0 },
      attachTo: document.body,
    })
    const img = document.querySelector('.lb-image') as HTMLImageElement
    expect(img).toBeTruthy()
    expect(img.src).toContain('img1.jpg')
    wrapper.unmount()
  })

  it('shows counter', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true, startIndex: 0 },
      attachTo: document.body,
    })
    const counter = document.querySelector('.lb-counter')
    expect(counter?.textContent).toContain('1 / 3')
    wrapper.unmount()
  })

  it('emits update:visible on close', async () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true },
      attachTo: document.body,
    })
    const closeBtn = document.querySelector('.lb-close') as HTMLElement
    expect(closeBtn).toBeTruthy()
    closeBtn.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:visible')).toBeTruthy()
    expect(wrapper.emitted('update:visible')![0]).toEqual([false])
    wrapper.unmount()
  })

  it('shows navigation buttons for multiple images', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true },
      attachTo: document.body,
    })
    expect(document.querySelector('.lb-prev')).toBeTruthy()
    expect(document.querySelector('.lb-next')).toBeTruthy()
    wrapper.unmount()
  })

  it('has proper dialog role', () => {
    const wrapper = mount(ImageLightbox, {
      props: { images, visible: true },
      attachTo: document.body,
    })
    const overlay = document.querySelector('.lightbox-overlay')
    expect(overlay?.getAttribute('role')).toBe('dialog')
    expect(overlay?.getAttribute('aria-modal')).toBe('true')
    wrapper.unmount()
  })
})
