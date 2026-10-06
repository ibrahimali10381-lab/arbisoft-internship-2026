import { describe, expect, it } from 'vitest'
import { countdownLabel, daysUntil, scoreLabel } from './format'

const NOW = new Date('2026-10-05T15:00:00')

describe('format helpers', () => {
  it('counts days to the exam', () => {
    expect(daysUntil('2026-10-15', NOW)).toBe(10)
    expect(daysUntil(null, NOW)).toBeNull()
  })

  it('labels the countdown', () => {
    expect(countdownLabel('2026-10-06', NOW)).toBe('1 day to exam')
    expect(countdownLabel('2026-10-05', NOW)).toBe('Exam today')
    expect(countdownLabel('2026-10-01', NOW)).toBe('Exam passed')
    expect(countdownLabel(null, NOW)).toBe('No exam date')
  })

  it('labels scores', () => {
    expect(scoreLabel(5)).toBe('Mastered')
    expect(scoreLabel(3)).toBe('Almost there')
    expect(scoreLabel(1)).toBe('Partly right')
    expect(scoreLabel(0)).toBe('Not yet')
  })
})
