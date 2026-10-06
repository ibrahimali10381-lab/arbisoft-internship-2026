export function MasteryBar({ value, label }: { value: number; label?: string }) {
  const pct = Math.round(value * 100)
  const tone = pct >= 75 ? 'good' : pct >= 40 ? 'mid' : 'weak'
  return (
    <div className="mastery" title={`${pct}% mastery`}>
      <div
        className={`mastery-fill ${tone}`}
        style={{ width: `${pct}%` }}
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label ?? 'mastery'}
      />
      <span className="mastery-label">{pct}%</span>
    </div>
  )
}

export function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <p className="error" role="alert">
      {message}
    </p>
  )
}

export function Spinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <p className="muted spinner" role="status">
      {label}
    </p>
  )
}
