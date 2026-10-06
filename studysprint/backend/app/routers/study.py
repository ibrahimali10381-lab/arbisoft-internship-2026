from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.ai.registry import registry
from app.db import get_db
from app.models import Course, Question, Topic, User
from app.routers.deps import owned_course, owned_question, owned_topic
from app.schemas import (
    AttemptCreate,
    AttemptRead,
    GenerateQuestionsRequest,
    PlanResponse,
    QuestionWithAnswer,
    SessionQuestion,
    SessionResponse,
)
from app.security import get_current_user

router = APIRouter(tags=["study"])


@router.post("/topics/{topic_id}/questions", response_model=list[QuestionWithAnswer])
def generate_questions(
    payload: GenerateQuestionsRequest,
    topic: Topic = Depends(owned_topic),
    db: Session = Depends(get_db),
) -> list[Question]:
    registry.call("generate_questions", db=db, topic=topic, count=payload.count)
    return topic.questions


@router.get("/topics/{topic_id}/questions", response_model=list[QuestionWithAnswer])
def list_questions(topic: Topic = Depends(owned_topic)) -> list[Question]:
    return topic.questions


@router.get("/courses/{course_id}/session", response_model=SessionResponse)
def get_session(
    size: int = Query(default=5, ge=1, le=15),
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SessionResponse:
    questions = registry.call("build_session", db=db, course=course, user=user, size=size)
    return SessionResponse(
        course_id=course.id,
        questions=[
            SessionQuestion(
                id=q.id,
                topic_id=q.topic_id,
                prompt=q.prompt,
                source_page=q.source_page,
                model=q.model,
                topic_name=q.topic.name,
                topic_mastery=q.topic.mastery,
            )
            for q in questions
        ],
    )


@router.post("/questions/{question_id}/attempts", response_model=AttemptRead, status_code=201)
def submit_attempt(
    payload: AttemptCreate,
    question: Question = Depends(owned_question),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AttemptRead:
    attempt = registry.call(
        "grade_answer", db=db, question=question, user=user, answer=payload.answer.strip()
    )
    return AttemptRead(
        id=attempt.id,
        question_id=question.id,
        score=attempt.score,
        feedback=attempt.feedback,
        missing_points=attempt.missing_points,
        model=attempt.model,
        created_at=attempt.created_at,
        reference_answer=question.reference_answer,
        source_page=question.source_page,
        topic_mastery=question.topic.mastery,
    )


@router.get("/courses/{course_id}/plan", response_model=PlanResponse)
def get_plan(course: Course = Depends(owned_course)) -> PlanResponse:
    days = registry.call("plan_sessions", course=course)
    return PlanResponse(course_id=course.id, exam_date=course.exam_date, days=days)
