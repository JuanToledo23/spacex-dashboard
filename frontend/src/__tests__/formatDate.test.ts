import { describe, it, expect } from 'vitest'
import { formatDate, formatDateShort } from '@/utils/formatDate'

describe('formatDate', () => {
  it('formats a valid ISO date string', () => {
    const result = formatDate('2023-06-15T10:00:00.000Z')
    expect(result).toContain('2023')
    expect(result).toContain('June')
    expect(result).toContain('15')
  })

  it('returns dash for null input', () => {
    expect(formatDate(null)).toBe('—')
  })

  it('returns dash for empty string', () => {
    expect(formatDate('')).toBe('—')
  })

  it('accepts custom options', () => {
    const result = formatDate('2023-06-15T10:00:00.000Z', { month: 'short' })
    expect(result).toContain('Jun')
  })
})

describe('formatDateShort', () => {
  it('uses short month format', () => {
    const result = formatDateShort('2023-06-15T10:00:00.000Z')
    expect(result).toContain('Jun')
    expect(result).toContain('15')
    expect(result).toContain('2023')
  })

  it('returns dash for null', () => {
    expect(formatDateShort(null)).toBe('—')
  })
})
