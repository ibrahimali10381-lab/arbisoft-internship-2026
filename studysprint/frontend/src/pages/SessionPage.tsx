import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { AttemptResult, SessionQuestion } from '../api/client'
import { ErrorBanner, MasteryBar, Spinner } from '../components/ui'
import { scoreLabel } from '../lib/format'

export function SessionPage() {
  const courseId = Number(useParams().courseId)
  const [questions, setQuestions] = useState<SessionQuestion[] | null>(null)
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [scores, setScores] = useState<number[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api
      .getSession(courseId, 5)
      .then((session) => setQuestions(session.questions))
      .catch((err: Error) => setError(err.message))
  }, [courseId])

  if (error && !questions) return <ErrorBanner message={error} />
  if (!questions) return <Spinner label="Picking your weakest topics…" />
  if (questions.length === 0) {
    return (
      <section className="card">
        <p>No questions yet — upload material first.</p>
        <Link to={`/courses/${courseId}`}>Back to course</Link>
      </section>
    )
  }

  const done = index >= questions.length
  if (done) {
    const total = scores.reduce((a, b) => a + b, 0)
    return (
      <section className="card narrow">
        <h1>Session complete</h1>
        <p>
          You scored {total} / {scores.length * 5}. Weak topics will come back sooner in your plan.
        </p>
        <Link className="button" to={`/courses/${courseId}`}>
          Back to course
        </Link>
      </section>
    )
  }

  const question = questions[index]

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!answer.trim()) {
      setError('Write an answer first — even a partial one helps.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const graded = await api.submitAttempt(question.id, answer.trim())
      setResult(graded)
      setScores((prev) => [...prev, graded.score])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Grading failed')
    } finally {
      setBusy(false)
    }
  }

  function next() {
    setIndex((i) => i + 1)
    setAnswer('')
    setResult(null)
  }

  return (
    <section className="card narrow">
      <p className="muted small">
        Question {index + 1} of {questions.length} · {question.topic_name} · page{' '}
        {question.source_page}
      </p>
      <h2>{question.prompt}</h2>
      <form onSubmit={onSubmit} className="stack">
        <textarea
          aria-label="Your answer"
          rows={5}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={Boolean(result)}
          placeholder="Answer in your own words…"
        />
        <ErrorBanner message={error} />
        {!result && (
          <button type="submit" disabled={busy}>
            {busy ? 'Grading…' : 'Submit answer'}
          </button>
        )}
      </form>

      {result && (
        <div className={`grade score-${result.score}`} aria-live="polite">
          <p className="score">
            {result.score} / 5 — {scoreLabel(result.score)}
          </p>
          <p>{result.feedback}</p>
          {result.missing_points.length > 0 && (
            <p>
              Missing: <strong>{result.missing_points.join(', ')}</strong>
            </p>
          )}
          <details>
            <summary>Source (page {result.source_page})</summary>
            <p className="muted">{result.reference_answer}</p>
          </details>
          <p className="small muted">Graded by {result.model}. Topic mastery is now:</p>
          <MasteryBar value={result.topic_mastery} label="Updated topic mastery" />
          <button type="button" onClick={next}>
            {index + 1 < questions.length ? 'Next question' : 'Finish'}
          </button>
        </div>
      )}
    </section>
  )
}
