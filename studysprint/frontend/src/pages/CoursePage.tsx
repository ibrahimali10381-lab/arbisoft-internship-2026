import { useCallback, useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { AgentRun, AskResult, CourseDetail, PlanDay } from '../api/client'
import { ErrorBanner, MasteryBar, Spinner } from '../components/ui'
import { countdownLabel } from '../lib/format'

export function CoursePage() {
  const courseId = Number(useParams().courseId)
  const navigate = useNavigate()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [plan, setPlan] = useState<PlanDay[]>([])
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [generating, setGenerating] = useState<number | null>(null)

  const refresh = useCallback(async () => {
    try {
      const [detail, planResult] = await Promise.all([
        api.getCourse(courseId),
        api.getPlan(courseId),
      ])
      setCourse(detail)
      setPlan(planResult.days)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load course')
    }
  }, [courseId])

  useEffect(() => {
    void refresh()
  }, [refresh])

  async function onUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    setUploading(true)
    setError(null)
    setNotice(null)
    try {
      const result = await api.uploadDocument(courseId, file)
      setNotice(
        `${result.document.filename}: ${result.document.page_count} pages, ` +
          `${result.topics_created} new topics (model: ${result.model}).`,
      )
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  async function onGenerate(topicId: number) {
    setGenerating(topicId)
    setError(null)
    try {
      await api.generateQuestions(topicId, 3)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not generate questions')
    } finally {
      setGenerating(null)
    }
  }

  async function onDelete() {
    if (!window.confirm('Delete this course and all its questions?')) return
    try {
      await api.deleteCourse(courseId)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete course')
    }
  }

  if (!course) return error ? <ErrorBanner message={error} /> : <Spinner label="Loading course…" />

  const hasTopics = course.topics.length > 0
  return (
    <div className="stack">
      <section className="card">
        <div className="row spread">
          <div>
            <h1>{course.title}</h1>
            <p className="muted">
              {countdownLabel(course.exam_date)} · average mastery{' '}
              {Math.round(course.average_mastery * 100)}%
            </p>
          </div>
          <div className="row">
            <Link
              to={`/courses/${course.id}/study`}
              className={`button ${hasTopics ? '' : 'disabled'}`}
              aria-disabled={!hasTopics}
              onClick={(e) => !hasTopics && e.preventDefault()}
            >
              Start today's session
            </Link>
            <button type="button" className="danger" onClick={onDelete}>
              Delete
            </button>
          </div>
        </div>
        <label className="upload">
          {uploading
            ? 'Reading your file and extracting topics…'
            : 'Upload a lecture (PDF, TXT, MD)'}
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={onUpload}
            disabled={uploading}
            aria-label="Upload course material"
          />
        </label>
        {course.documents.length > 0 && (
          <p className="muted small">
            Files: {course.documents.map((d) => `${d.filename} (${d.page_count}p)`).join(', ')}
          </p>
        )}
        {notice && <p className="notice">{notice}</p>}
        <ErrorBanner message={error} />
      </section>

      <section className="card">
        <h2>Topics</h2>
        {!hasTopics && <p className="muted">Upload material to map your topics.</p>}
        <table className="topics">
          <tbody>
            {course.topics.map((topic) => (
              <tr key={topic.id}>
                <td>
                  <strong>{topic.name}</strong>
                  <div className="muted small">
                    p.{topic.source_page} · {topic.attempts} attempts · {topic.question_count}{' '}
                    questions
                  </div>
                </td>
                <td className="bar-cell">
                  <MasteryBar value={topic.mastery} label={`${topic.name} mastery`} />
                </td>
                <td>
                  <button
                    type="button"
                    className="secondary"
                    disabled={generating !== null}
                    onClick={() => onGenerate(topic.id)}
                  >
                    {generating === topic.id ? 'Writing…' : '+3 questions'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {plan.length > 0 && (
        <section className="card">
          <h2>Study plan</h2>
          <ol className="plan">
            {plan.map((day) => (
              <li key={day.date}>
                <span className={`tag ${day.focus}`}>{day.focus}</span>
                <strong>{new Date(`${day.date}T00:00:00`).toDateString()}</strong>
                <span className="muted"> — {day.topics.map((t) => t.name).join(', ')}</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      <div className="grid two">
        <AskPanel courseId={courseId} />
        <AgentPanel courseId={courseId} onDone={refresh} />
      </div>
    </div>
  )
}

function AskPanel({ courseId }: { courseId: number }) {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<AskResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onAsk(event: FormEvent) {
    event.preventDefault()
    if (question.trim().length < 3) return
    setBusy(true)
    setError(null)
    try {
      setResult(await api.ask(courseId, question.trim()))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not answer')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <h2>Ask your material</h2>
      <form onSubmit={onAsk} className="row">
        <input
          aria-label="Question about the material"
          placeholder="What causes thrashing?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={busy}>
          {busy ? 'Searching…' : 'Ask'}
        </button>
      </form>
      <ErrorBanner message={error} />
      {result && (
        <div className="answer">
          <p>{result.answer}</p>
          {result.citations.map((c) => (
            <p key={`${c.document}-${c.page}`} className="muted small">
              {c.document}, page {c.page}
            </p>
          ))}
          <p className="muted small">
            model: {result.model}
            {result.cached ? ' (cached)' : ''}
          </p>
        </div>
      )}
    </section>
  )
}

function AgentPanel({ courseId, onDone }: { courseId: number; onDone: () => Promise<void> }) {
  const [goal, setGoal] = useState('Get me ready for the exam')
  const [run, setRun] = useState<AgentRun | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onRun(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      setRun(await api.runAgent(courseId, goal))
      await onDone()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Agent failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card">
      <h2>Study agent</h2>
      <p className="muted small">Try “quiz me”, “make a schedule”, or a question.</p>
      <form onSubmit={onRun} className="row">
        <input aria-label="Agent goal" value={goal} onChange={(e) => setGoal(e.target.value)} />
        <button type="submit" disabled={busy || goal.trim().length < 3}>
          {busy ? 'Running…' : 'Run'}
        </button>
      </form>
      <ErrorBanner message={error} />
      {run && (
        <div className="answer">
          <p>
            Intent: <strong>{run.intent}</strong> ·{' '}
            <Link to={`/traces?run=${run.run_id}`}>view trace</Link>
          </p>
          <ol>
            {run.steps.map((step, i) => (
              <li key={i}>
                <code>{step.worker}</code> → <code>{step.tool}</code>: {step.summary}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}
