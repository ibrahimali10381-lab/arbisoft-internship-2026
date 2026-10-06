import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { SessionPage } from './SessionPage'

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const question = {
  id: 7,
  topic_id: 2,
  prompt: 'What is a deadlock?',
  source_page: 4,
  model: 'local-keyword',
  topic_name: 'Deadlocks',
  topic_mastery: 0,
}

function renderSession() {
  render(
    <MemoryRouter initialEntries={['/courses/1/study']}>
      <Routes>
        <Route path="/courses/:courseId/study" element={<SessionPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

afterEach(() => vi.restoreAllMocks())

describe('SessionPage', () => {
  it('grades an answer and shows feedback, missing points and new mastery', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ course_id: 1, questions: [question] }))
      .mockResolvedValueOnce(
        jsonResponse({
          id: 1,
          question_id: 7,
          score: 3,
          feedback: 'Good answer. To make it complete, also mention: held.',
          missing_points: ['held'],
          model: 'local-keyword',
          reference_answer: 'A deadlock is when processes wait for resources held by others.',
          source_page: 4,
          topic_mastery: 0.6,
        }),
      )
    renderSession()

    expect(await screen.findByRole('heading', { name: 'What is a deadlock?' })).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Your answer'), 'processes wait for resources')
    await userEvent.click(screen.getByRole('button', { name: 'Submit answer' }))

    expect(await screen.findByText('3 / 5 — Almost there')).toBeInTheDocument()
    expect(screen.getByText('held')).toBeInTheDocument()
    expect(screen.getByRole('progressbar', { name: 'Updated topic mastery' })).toHaveAttribute(
      'aria-valuenow',
      '60',
    )
    const [, init] = fetchMock.mock.calls[1]
    expect(JSON.parse(String(init?.body))).toEqual({ answer: 'processes wait for resources' })

    await userEvent.click(screen.getByRole('button', { name: 'Finish' }))
    expect(screen.getByText(/You scored 3 \/ 5/)).toBeInTheDocument()
  })

  it('requires an answer before grading', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      jsonResponse({ course_id: 1, questions: [question] }),
    )
    renderSession()
    await userEvent.click(await screen.findByRole('button', { name: 'Submit answer' }))
    expect(screen.getByRole('alert')).toHaveTextContent('Write an answer first')
  })

  it('shows API errors', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      jsonResponse({ detail: 'Course not found' }, 404),
    )
    renderSession()
    expect(await screen.findByRole('alert')).toHaveTextContent('Course not found')
  })
})
