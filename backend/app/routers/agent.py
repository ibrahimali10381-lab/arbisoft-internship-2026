from fastapi import APIRouter, Depends, HTTPException, status

from app import models, schemas
from app.agent import research_agent
from app.agent.memory import memory_store
from app.security import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/research", response_model=schemas.AgentResearchResponse)
def run_research(
    payload: schemas.AgentResearchRequest,
    _: models.User = Depends(get_current_user),
) -> schemas.AgentResearchResponse:
    try:
        result = research_agent.run(query=payload.query, session_id=payload.session_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return schemas.AgentResearchResponse(
        session_id=result.session_id,
        query=result.query,
        plan=result.plan,
        answer=result.answer,
        sources=[
            schemas.SearchResult(title=s.title, link=s.link, snippet=s.snippet)
            for s in result.sources
        ],
        remembered_facts=result.remembered_facts,
        memory_used=result.memory_used,
    )


@router.get("/memory/{session_id}", response_model=schemas.AgentMemoryResponse)
def get_memory(
    session_id: str,
    _: models.User = Depends(get_current_user),
) -> schemas.AgentMemoryResponse:
    return schemas.AgentMemoryResponse(
        session_id=session_id,
        facts=memory_store.all_facts(session_id),
    )


@router.post("/memory", response_model=schemas.AgentMemoryResponse)
def remember_fact(
    payload: schemas.AgentRememberRequest,
    _: models.User = Depends(get_current_user),
) -> schemas.AgentMemoryResponse:
    memory_store.remember(payload.session_id, payload.fact)
    return schemas.AgentMemoryResponse(
        session_id=payload.session_id,
        facts=memory_store.all_facts(payload.session_id),
    )
