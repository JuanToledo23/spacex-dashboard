import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from '@/components/common/DataTable.vue'

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
]

const rows = [
  { id: '1', name: 'Alpha', status: 'active' },
  { id: '2', name: 'Beta', status: 'retired' },
]

describe('DataTable', () => {
  it('renders column headers', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const headers = wrapper.findAll('th')
    expect(headers).toHaveLength(2)
    expect(headers[0].text()).toBe('Name')
    expect(headers[1].text()).toBe('Status')
  })

  it('renders rows', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const tds = wrapper.findAll('tbody td')
    expect(tds).toHaveLength(4)
    expect(tds[0].text()).toBe('Alpha')
  })

  it('shows empty state when no rows', () => {
    const wrapper = mount(DataTable, { props: { columns, rows: [] } })
    expect(wrapper.text()).toContain('NO DATA')
  })

  it('shows pagination when total > limit', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, total: 40, page: 1, limit: 20 },
    })
    expect(wrapper.find('nav').exists()).toBe(true)
    expect(wrapper.text()).toContain('1')
    expect(wrapper.text()).toContain('2')
  })

  it('hides pagination when total <= limit', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, total: 2, page: 1, limit: 20 },
    })
    expect(wrapper.find('nav').exists()).toBe(false)
  })

  it('emits page-change on nav click', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, total: 40, page: 1, limit: 20 },
    })
    const nextBtn = wrapper.findAll('button').find(b => b.text() === 'NEXT')
    await nextBtn!.trigger('click')
    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')![0]).toEqual([2])
  })

  it('emits row-click when clickable', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, clickable: true },
    })
    const firstRow = wrapper.find('tbody tr')
    await firstRow.trigger('click')
    expect(wrapper.emitted('row-click')).toBeTruthy()
    expect(wrapper.emitted('row-click')![0][0]).toEqual(rows[0])
  })

  it('does not emit row-click when not clickable', async () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, clickable: false },
    })
    const firstRow = wrapper.find('tbody tr')
    await firstRow.trigger('click')
    expect(wrapper.emitted('row-click')).toBeFalsy()
  })

  it('disables prev button on first page', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, total: 40, page: 1, limit: 20 },
    })
    const prevBtn = wrapper.findAll('button').find(b => b.text() === 'PREV')
    expect(prevBtn!.attributes('disabled')).toBeDefined()
  })

  it('disables next button on last page', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, total: 40, page: 2, limit: 20 },
    })
    const nextBtn = wrapper.findAll('button').find(b => b.text() === 'NEXT')
    expect(nextBtn!.attributes('disabled')).toBeDefined()
  })

  it('uses default value for missing cell data', () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [{ id: '1', name: 'Test' }] },
    })
    const cells = wrapper.findAll('tbody td')
    expect(cells[1].text()).toBe('—')
  })
})
