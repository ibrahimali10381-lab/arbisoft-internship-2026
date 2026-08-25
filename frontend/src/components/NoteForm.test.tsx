import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { NoteForm } from './NoteForm'
import { validateNoteForm } from './noteValidation'

const users = [
  { id: 1, username: 'demo' },
  { id: 2, username: 'alice' },
]

describe('validateNoteForm', () => {
  it('requires a title of at least 3 characters', () => {
    expect(validateNoteForm({ title: 'ab', content: 'long enough', owner_id: 1 })).toEqual({
      title: 'Title must be at least 3 characters',
    })
  })

  it('requires content of at least 5 characters', () => {
    expect(validateNoteForm({ title: 'Hello', content: 'hi', owner_id: 1 })).toEqual({
      content: 'Content must be at least 5 characters',
    })
  })

  it('requires a valid owner id', () => {
    expect(validateNoteForm({ title: 'Hello', content: 'long enough', owner_id: 0 })).toEqual({
      owner_id: 'Select an owner',
    })
  })
})

describe('NoteForm', () => {
  it('shows validation errors and does not submit invalid data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<NoteForm users={users} onSubmit={onSubmit} />)

    await user.click(screen.getByRole('button', { name: /create note/i }))

    expect(screen.getByText('Title is required')).toBeInTheDocument()
    expect(screen.getByText('Content is required')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submits trimmed values when the form is valid', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    render(<NoteForm users={users} onSubmit={onSubmit} />)

    await user.type(screen.getByRole('textbox', { name: /^title$/i }), '  Meeting notes  ')
    await user.type(
      screen.getByRole('textbox', { name: /^content$/i }),
      '  Discuss internship tasks  ',
    )
    await user.selectOptions(screen.getByRole('combobox', { name: /^owner$/i }), '2')
    await user.click(screen.getByRole('button', { name: /create note/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Meeting notes',
      content: 'Discuss internship tasks',
      owner_id: 2,
    })
  })
})
