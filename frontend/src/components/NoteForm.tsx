import { useMemo, useState, type FormEvent } from 'react'
import { validateNoteForm, type NoteFormErrors, type NoteFormValues } from './noteValidation'

type NoteFormProps = {
  onSubmit: (values: NoteFormValues) => Promise<void> | void
  submitLabel?: string
}

export function NoteForm({ onSubmit, submitLabel = 'Create note' }: NoteFormProps) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [errors, setErrors] = useState<NoteFormErrors>({})
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const values = useMemo(() => ({ title, content }), [title, content])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const nextErrors = validateNoteForm(values)
    setErrors(nextErrors)
    setFormError(null)

    if (Object.keys(nextErrors).length > 0) {
      return
    }

    setSubmitting(true)
    try {
      await onSubmit({
        title: title.trim(),
        content: content.trim(),
      })
      setTitle('')
      setContent('')
      setErrors({})
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to save note')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="note-form" onSubmit={handleSubmit} noValidate>
      <label className="field">
        <span>Title</span>
        <input
          name="title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          aria-invalid={Boolean(errors.title)}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        {errors.title ? (
          <p id="title-error" className="field-error" role="alert">
            {errors.title}
          </p>
        ) : null}
      </label>

      <label className="field">
        <span>Content</span>
        <textarea
          name="content"
          rows={6}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          aria-invalid={Boolean(errors.content)}
          aria-describedby={errors.content ? 'content-error' : undefined}
        />
        {errors.content ? (
          <p id="content-error" className="field-error" role="alert">
            {errors.content}
          </p>
        ) : null}
      </label>

      {formError ? (
        <p className="form-error" role="alert">
          {formError}
        </p>
      ) : null}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Saving…' : submitLabel}
      </button>
    </form>
  )
}
