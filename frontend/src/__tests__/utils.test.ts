import { describe, it, expect } from 'vitest'
import { formatDate, formatDuration, statusColor, statusBadgeClass } from '../lib/utils'

describe('formatDate', () => {
  it('returns formatted date for valid ISO string', () => {
    const result = formatDate('2026-11-19T10:30:00Z')
    expect(result).toContain('2026')
    expect(result).toContain('Nov')
  })

  it('returns em-dash for null/undefined', () => {
    expect(formatDate(null)).toBe('—')
    expect(formatDate(undefined)).toBe('—')
  })
})

describe('formatDuration', () => {
  it('formats milliseconds correctly', () => {
    expect(formatDuration(0.5)).toMatch(/\d+ms/)
  })

  it('formats seconds correctly', () => {
    expect(formatDuration(45)).toMatch(/45\.0s/)
  })

  it('formats minutes correctly', () => {
    expect(formatDuration(120)).toMatch(/2m/)
  })

  it('returns em-dash for null', () => {
    expect(formatDuration(null)).toBe('—')
    expect(formatDuration(undefined)).toBe('—')
  })
})

describe('statusColor', () => {
  it('returns correct color for COMPLETED', () => {
    expect(statusColor('COMPLETED')).toBe('text-emerald-400')
  })

  it('returns correct color for RUNNING', () => {
    expect(statusColor('RUNNING')).toBe('text-blue-400')
  })

  it('returns correct color for FAILED', () => {
    expect(statusColor('FAILED')).toBe('text-red-400')
  })

  it('returns default for unknown status', () => {
    expect(statusColor('UNKNOWN')).toBe('text-muted-foreground')
  })
})

describe('statusBadgeClass', () => {
  it('returns correct class for COMPLETED', () => {
    expect(statusBadgeClass('COMPLETED')).toContain('bg-emerald')
  })

  it('returns correct class for PENDING', () => {
    expect(statusBadgeClass('PENDING')).toContain('bg-gray')
  })
})
