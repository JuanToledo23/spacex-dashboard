import { describe, it, expect } from 'vitest'
import { getCssVar } from '@/utils/chartColors'

describe('getCssVar', () => {
  it('returns empty string for undefined CSS variable', () => {
    const result = getCssVar('--nonexistent-var')
    expect(typeof result).toBe('string')
  })

  it('returns trimmed value', () => {
    document.documentElement.style.setProperty('--test-color', '  #ff0000  ')
    const result = getCssVar('--test-color')
    expect(result).toBe('#ff0000')
    document.documentElement.style.removeProperty('--test-color')
  })

  it('returns empty string when not set', () => {
    const result = getCssVar('--definitely-not-set')
    expect(result).toBe('')
  })
})
