import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api/client'
import type { CompareRow, Course, ModelInfo, QuestionWithAnswer } from '../api/client'
import { ErrorBanner, Spinner } from '../components/ui'

export function ComparePage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [models, setModels] = useState<ModelInfo[] | null>(null)
  const [courseId, setCourseId] = useState<number | null>(null)
  const [task, setTask] = useState<'ask' | 'grade'>('ask')
  const [question, setQuestion] = useState('What is virtual memory?')
  const [questions, setQuestions] = useState<QuestionWithAnswer[]>([])
  const [questionId, setQuestionId] = useState<number | null>(null)
  const [answer, setAnswer] = useState('')
  const [selected, setSelected] = useState<string[]>([])
  const [rows, setRows] = useState<CompareRow[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    Promise.all([api.listCourses(), api.listModels()])
      .then(([courseList, modelList]) => {
        setCourses(courseList)
        setModels(modelList)
        setSelected(modelList.filter((m) => m.available).map((m) => m.id))
        if (courseList[0]) setCourseId(courseList[0].id)
      })
      .catch((err: Error) => setError(err.message))
  }, [])

  useEffect(() => {
    if (task !== 'grade' || courseId === null) return
    api
      .getCourse(courseId)
      .then(async (course) => {
        const lists = await Promise.all(course.topics.map((t) => api.listQuestions(t.id)))
        const all = lists.flat()
        setQuestions(all)
        setQuestionId(all[0]?.id ?? null)
      })
      .catch((err: Error) => setError(err.message))
  }, [task, courseId])

  function toggle(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]))
  }

  async function onRun(event: FormEvent) {
    event.preventDefault()
    if (courseId === null) return
    if (selected.length < 2) {
      setError('Pick at least two models to compare.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const result = await api.compare(
        task === 'ask'
          ? { task, course_id: courseId, question, models: selected }
          : { task, course_id: courseId, question_id: questionId ?? 0, answer, models: selected },
      )
      setRows(result.rows)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed')
    } finally {
      setBusy(false)
    }
  }

  if (!models) return error ? <ErrorBanner message={error} /> : <Spinner />

  return (
    <div className="stack">
      <section className="card">
        <h1>Compare models</h1>
        <p className="muted">
          Send the same request to several models and compare output, validity and latency.
        </p>
        <form className="stack" onSubmit={onRun}>
          <div className="row">
            <select
              aria-label="Course"
              value={courseId ?? ''}
              onChange={(e) => setCourseId(Number(e.target.value))}
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
            <select
              aria-label="Task"
              value={task}
              onChange={(e) => setTask(e.target.value as 'ask' | 'grade')}
            >
              <option value="ask">Answer a question (RAG)</option>
              <option value="grade">Grade an answer</option>
            </select>
          </div>
          {task === 'ask' ? (
            <input
              aria-label="Question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          ) : (
            <>
              <select
                aria-label="Quiz question"
                value={questionId ?? ''}
                onChange={(e) => setQuestionId(Number(e.target.value))}
              >
                {questions.map((q) => (
                  <option key={q.id} value={q.id}>
                    {q.prompt}
                  </option>
                ))}
              </select>
              <textarea
                aria-label="Student answer"
                rows={3}
                placeholder="Student answer to grade"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
              />
            </>
          )}
          <fieldset className="row">
            <legend className="small muted">Models</legend>
            {models.map((m) => (
              <label key={m.id} className={`chip ${m.available ? '' : 'off'}`}>
                <input
                  type="checkbox"
                  checked={selected.includes(m.id)}
                  onChange={() => toggle(m.id)}
                />
                {m.label}
                {!m.available && ' (not configured)'}
              </label>
            ))}
          </fieldset>
          <ErrorBanner message={error} />
          <button type="submit" disabled={busy || courseId === null}>
            {busy ? 'Running…' : 'Run comparison'}
          </button>
        </form>
      </section>

      {rows && (
        <div className="grid">
          {rows.map((row) => (
            <section key={row.model} className={`card ${row.ok ? '' : 'failed'}`}>
              <h2>{row.model}</h2>
              <p className="muted small">{row.latency_ms} ms</p>
              {row.ok ? (
                <pre>{JSON.stringify(row.output, null, 2)}</pre>
              ) : (
                <p className="error">{row.error}</p>
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
