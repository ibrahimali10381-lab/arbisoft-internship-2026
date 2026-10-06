from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.registry import registry
from app.config import settings
from app.db import get_db
from app.models import Course, Topic, User
from app.routers.deps import owned_course
from app.schemas import (
    CourseCreate,
    CourseDetail,
    CourseRead,
    CourseUpdate,
    DocumentRead,
    TopicRead,
    UploadResponse,
)
from app.security import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])


def topic_read(topic: Topic) -> TopicRead:
    return TopicRead.model_validate(topic).model_copy(
        update={"question_count": len(topic.questions)}
    )


def course_read(course: Course) -> CourseRead:
    topics = course.topics
    avg = sum(t.mastery for t in topics) / len(topics) if topics else 0.0
    return CourseRead.model_validate(course).model_copy(
        update={
            "document_count": len(course.documents),
            "topic_count": len(topics),
            "average_mastery": round(avg, 3),
        }
    )


def course_detail(course: Course) -> CourseDetail:
    return CourseDetail(
        **course_read(course).model_dump(),
        documents=[DocumentRead.model_validate(d) for d in course.documents],
        topics=[topic_read(t) for t in course.topics],
    )


@router.get("", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[CourseRead]:
    courses = db.scalars(
        select(Course).where(Course.owner_id == user.id).order_by(Course.created_at.desc())
    )
    return [course_read(c) for c in courses]


@router.post("", response_model=CourseDetail, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> CourseDetail:
    course = Course(owner_id=user.id, title=payload.title.strip(), exam_date=payload.exam_date)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course_detail(course)


@router.get("/{course_id}", response_model=CourseDetail)
def get_course(course: Course = Depends(owned_course)) -> CourseDetail:
    return course_detail(course)


@router.patch("/{course_id}", response_model=CourseDetail)
def update_course(
    payload: CourseUpdate,
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
) -> CourseDetail:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course_detail(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course: Course = Depends(owned_course), db: Session = Depends(get_db)
) -> Response:
    db.delete(course)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{course_id}/documents", response_model=UploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile,
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
) -> UploadResponse:
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE, f"File exceeds {settings.max_upload_mb} MB"
        )
    result = registry.call(
        "ingest_document", db=db, course=course, filename=file.filename or "upload", data=data
    )
    return UploadResponse(
        document=DocumentRead.model_validate(result["document"]),
        topics_created=result["topics_created"],
        model=result["model"],
    )


@router.get("/{course_id}/topics", response_model=list[TopicRead])
def list_topics(course: Course = Depends(owned_course)) -> list[TopicRead]:
    return [topic_read(t) for t in course.topics]
