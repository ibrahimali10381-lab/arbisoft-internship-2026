from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


def _can_manage_note(user: models.User, note: models.Note) -> bool:
    return user.role == "admin" or note.owner_id == user.id


@router.post("", response_model=schemas.NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: schemas.NoteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.Note:
    note = models.Note(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[schemas.NoteRead])
def list_notes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[models.Note]:
    query = db.query(models.Note)
    if current_user.role != "admin":
        query = query.filter(models.Note.owner_id == current_user.id)
    return query.order_by(models.Note.id.desc()).all()


@router.get("/{note_id}", response_model=schemas.NoteRead)
def get_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.Note:
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if not _can_manage_note(current_user, note):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return note


@router.put("/{note_id}", response_model=schemas.NoteRead)
def update_note(
    note_id: int,
    payload: schemas.NoteUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.Note:
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if not _can_manage_note(current_user, note):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """RBAC: owners can delete own notes; admins can delete any note."""
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if not _can_manage_note(current_user, note):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this note",
        )
    db.delete(note)
    db.commit()
