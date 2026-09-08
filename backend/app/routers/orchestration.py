from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.agent.multi_hop import multi_hop_agent
from app.agent.supervisor import supervisor_agent
from app.agent.tracing import trace_store
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


@router.post("/supervise", response_model=schemas.SupervisorResponse)
def supervise(
    payload: schemas.SupervisorRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.SupervisorResponse:
    result = supervisor_agent.run(
        query=payload.query,
        db=db,
        session_id=payload.session_id,
        owner_id=None if current_user.role == "admin" else current_user.id,
        file_path=payload.file_path,
    )
    return schemas.SupervisorResponse(
        query=result.query,
        route=result.route,
        answer=result.answer,
        handoffs=[
            schemas.WorkerHandoff(
                worker=h.worker,
                summary=h.summary,
                details=h.details,
            )
            for h in result.handoffs
        ],
        traces=trace_store.list_events(limit=50),
    )


@router.post("/multi-hop", response_model=schemas.MultiHopResponse)
def multi_hop(
    payload: schemas.MultiHopRequest,
    _: models.User = Depends(get_current_user),
) -> schemas.MultiHopResponse:
    result = multi_hop_agent.run(question=payload.question, session_id=payload.session_id)
    return schemas.MultiHopResponse(
        question=result.question,
        steps=result.steps,
        answer=result.answer,
        session_id=result.session_id,
        traces=trace_store.list_events(limit=50),
    )


@router.get("/traces", response_model=schemas.TraceListResponse)
def list_traces(
    _: models.User = Depends(get_current_user),
) -> schemas.TraceListResponse:
    return schemas.TraceListResponse(events=trace_store.list_events(limit=200))


@router.delete("/traces", status_code=204)
def clear_traces(_: models.User = Depends(get_current_user)) -> None:
    trace_store.clear()
