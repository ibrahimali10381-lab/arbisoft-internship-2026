export function daysUntil(isoDate: string | null, now: Date = new Date()): number | null {
  if (!isoDate) return null
  const today = new Date(now)
  today.setHours(0, 0, 0, 0)
  const exam = new Date(`${isoDate}T00:00:00`)
  return Math.round((exam.getTime() - today.getTime()) / 86_400_000)
}

export function countdownLabel(isoDate: string | null, now?: Date): string {
  const days = daysUntil(isoDate, now)
  if (days === null) return 'No exam date'
  if (days < 0) return 'Exam passed'
  if (days === 0) return 'Exam today'
  return `${days} day${days === 1 ? '' : 's'} to exam`
}

export function scoreLabel(score: number): string {
  if (score === 5) return 'Mastered'
  if (score >= 3) return 'Almost there'
  if (score >= 1) return 'Partly right'
  return 'Not yet'
}
