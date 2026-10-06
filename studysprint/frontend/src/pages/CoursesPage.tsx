import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Course } from '../api/client'
import { ErrorBanner, MasteryBar, Spinner } from '../components/ui'
import { countdownLabel } from '../lib/format'

export function CoursesPage() {
  const navigate = useNavigate()
  const [courses, setCourses] = useState<Course[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [title, setTitle] = useState('')
  const [examDate, setExamDate] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api
      .listCourses()
      .then(setCourses)
      .catch((err: Error) => setError(err.message))
  }, [])

  async function onCreate(event: FormEvent) {
    event.preventDefault()
    if (title.trim().length < 2) {
      setError('Course title must be at least 2 characters.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const course = await api.createCourse(title.trim(), examDate || null)
      navigate(`/courses/${course.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create course')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <section className="card">
        <h1>Your courses</h1>
        <form className="row" onSubmit={onCreate}>
          <input
            aria-label="Course title"
            placeholder="e.g. Operating Systems"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            aria-label="Exam date"
            type="date"
            value={examDate}
            onChange={(e) => setExamDate(e.target.value)}
          />
          <button type="submit" disabled={busy}>
            {busy ? 'Creating…' : 'Add course'}
          </button>
        </form>
        <ErrorBanner message={error} />
      </section>

      {courses === null && !error && <Spinner label="Loading courses…" />}
      {courses?.length === 0 && (
        <p className="muted">No courses yet. Add one above, then upload your lecture PDFs.</p>
      )}
      <div className="grid">
        {courses?.map((course) => (
          <Link key={course.id} to={`/courses/${course.id}`} className="card course-card">
            <h2>{course.title}</h2>
            <p className="muted small">
              {countdownLabel(course.exam_date)} · {course.document_count} files ·{' '}
              {course.topic_count} topics
            </p>
            <MasteryBar value={course.average_mastery} label={`${course.title} mastery`} />
          </Link>
        ))}
      </div>
    </div>
  )
}
