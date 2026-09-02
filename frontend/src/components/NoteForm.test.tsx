import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { NoteForm } from './NoteForm'
import { validateNoteForm } from './noteValidation'

describe('validateNoteForm', () => {
  it('requires a title of at least 3 characters', () => {
    expect(validateNoteForm({ title: 'ab', content: 'long enough' })).toEqual({
      title: 'Title must be at least 3 characters',
    })
  })

  it('requires content of at least 5 characters', () => {
    expect(validateNoteForm({ title: 'Hello', content: 'hi' })).toEqual({
      content: 'Content must be at least 5 characters',
    })
  })

  it('accepts a valid note payload', () => {
    expect(validateNoteForm({ title: 'Hello', content: 'long enough' })).toEqual({})
  })
})

describe('NoteForm', () => {
  it('shows validation errors and does not submit invalid data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<NoteForm onSubmit={onSubmit} />)

    await user.click(screen.getByRole('button', { name: /create note/i }))

    expect(screen.getByText('Title is required')).toBeInTheDocument()
    expect(screen.getByText('Content is required')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submits trimmed values when the form is valid', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    render(<NoteForm onSubmit={onSubmit} />)

    await user.type(screen.getByRole('textbox', { name: /^title$/i }), '  Meeting notes  ')
    await user.type(
      screen.getByRole('textbox', { name: /^content$/i }),
      '  Discuss internship tasks  ',
    )
    await user.click(screen.getByRole('button', { name: /create note/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Meeting notes',
      content: 'Discuss internship tasks',
    })
  })
})
