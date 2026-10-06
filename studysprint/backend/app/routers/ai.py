from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.ai.agents import supervisor
from app.ai.outputs import AnswerOutput, GradeOutput, grade_guard, pages_guard
from app.ai.registry import registry
from app.ai.router import router as model_router
from app.ai.tracing import traces
from app.db import get_db
from app.models import Course, Question, User
from app.routers.deps import load_owned_course, owned_course
from app.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AskRequest,
    AskResponse,
    CompareRequest,
    CompareResponse,
    ModelInfo,
    ToolInfo,
    TraceEvent,
)
from app.security import get_current_user
from app.services.retrieval import retrieve

router = APIRouter(tags=["ai"])


@router.get("/ai/models", response_model=list[ModelInfo])
def list_models(_: User = Depends(get_current_user)) -> list[ModelInfo]:
    return [
        ModelInfo(id=p.id, label=p.label, kind=p.kind, available=p.available)
        for p in model_router.providers.values()
    ]


@router.get("/ai/tools", response_model=list[ToolInfo])
def list_tools(_: User = Depends(get_current_user)) -> list[dict]:
    return registry.describe()


@router.post("/courses/{course_id}/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
) -> dict:
    return registry.call(
        "answer_question", db=db, course=course, question=payload.question, model=payload.model
    )


@router.post("/ai/compare", response_model=CompareResponse)
def compare(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CompareResponse:
    course = load_owned_course(db, user, payload.course_id)
    unknown = [m for m in payload.models or [] if m not in model_router.providers]
    if unknown:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"Unknown models: {unknown}")

    if payload.task == "ask":
        if not payload.question:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "question is required")
        passages = retrieve(db, course.id, payload.question, k=5)
        if not passages:
            raise HTTPException(status.HTTP_409_CONFLICT, "Upload course material first")
        rows = model_router.compare(
            "answer_question",
            {
                "question": payload.question,
                "passages": [{"page": p["page"], "text": p["text"]} for p in passages],
            },
            AnswerOutput,
            pages_guard({p["page"] for p in passages}),
            payload.models,
        )
    else:
        question = db.get(Question, payload.question_id or 0)
        if question is None or question.topic.course_id != course.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found in this course")
        if not payload.answer:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "answer is required")
        rows = model_router.compare(
            "grade_answer",
            {
                "question": question.prompt,
                "reference_answer": question.reference_answer,
                "key_points": question.key_points,
                "source_page": question.source_page,
                "answer": payload.answer,
            },
            GradeOutput,
            grade_guard(question.key_points),
            payload.models,
        )
    return CompareResponse(task=payload.task, rows=rows)


@router.post("/agent/run", response_model=AgentRunResponse)
def run_agent(
    payload: AgentRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    course = load_owned_course(db, user, payload.course_id)
    return supervisor.run(db, course, user, payload.goal)


@router.get("/traces", response_model=list[TraceEvent])
def list_traces(
    limit: int = Query(default=100, ge=1, le=500),
    run_id: str | None = None,
    _: User = Depends(get_current_user),
) -> list[dict]:
    return traces.list(limit=limit, run_id=run_id)


@router.delete("/traces", status_code=status.HTTP_204_NO_CONTENT)
def clear_traces(_: User = Depends(get_current_user)) -> Response:
    traces.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
