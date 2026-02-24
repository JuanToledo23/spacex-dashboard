/**
 * Format a UTC date string for display.
 */
export function formatDate(dateStr: string | null, opts: Intl.DateTimeFormatOptions = {}): string {
  if (!dateStr) return '—'
  const defaults: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString('en-US', { ...defaults, ...opts })
}

export function formatDateShort(dateStr: string | null): string {
  return formatDate(dateStr, { month: 'short' })
}
