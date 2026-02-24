import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'

describe('SkeletonLoader', () => {
  it('renders 1 skeleton by default', () => {
    const wrapper = mount(SkeletonLoader)
    const skeletons = wrapper.findAll('.skeleton')
    expect(skeletons).toHaveLength(1)
  })

  it('renders N skeletons when count is set', () => {
    const wrapper = mount(SkeletonLoader, { props: { count: 5 } })
    const skeletons = wrapper.findAll('.skeleton')
    expect(skeletons).toHaveLength(5)
  })

  it('applies custom height', () => {
    const wrapper = mount(SkeletonLoader, { props: { height: '40px' } })
    const skeleton = wrapper.find('.skeleton')
    expect(skeleton.attributes('style')).toContain('height: 40px')
  })

  it('applies custom width', () => {
    const wrapper = mount(SkeletonLoader, { props: { width: '50%' } })
    const skeleton = wrapper.find('.skeleton')
    expect(skeleton.attributes('style')).toContain('width: 50%')
  })

  it('uses default dimensions', () => {
    const wrapper = mount(SkeletonLoader)
    const skeleton = wrapper.find('.skeleton')
    const style = skeleton.attributes('style')
    expect(style).toContain('height: 20px')
    expect(style).toContain('width: 100%')
  })
})
