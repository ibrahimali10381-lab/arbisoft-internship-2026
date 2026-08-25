export type NoteFormValues = {
  title: string
  content: string
  owner_id: number
}

export type NoteFormErrors = {
  title?: string
  content?: string
  owner_id?: string
}

export function validateNoteForm(values: NoteFormValues): NoteFormErrors {
  const errors: NoteFormErrors = {}

  if (!values.title.trim()) {
    errors.title = 'Title is required'
  } else if (values.title.trim().length < 3) {
    errors.title = 'Title must be at least 3 characters'
  } else if (values.title.trim().length > 200) {
    errors.title = 'Title must be 200 characters or fewer'
  }

  if (!values.content.trim()) {
    errors.content = 'Content is required'
  } else if (values.content.trim().length < 5) {
    errors.content = 'Content must be at least 5 characters'
  }

  if (!Number.isInteger(values.owner_id) || values.owner_id <= 0) {
    errors.owner_id = 'Select an owner'
  }

  return errors
}
