from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10_000)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=10_000)


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class AgentResearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    session_id: str = Field(min_length=1, max_length=100, default="default")


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str


class AgentResearchResponse(BaseModel):
    session_id: str
    query: str
    plan: list[str]
    answer: str
    sources: list[SearchResult]
    remembered_facts: list[str]
    memory_used: list[str]


class AgentMemoryResponse(BaseModel):
    session_id: str
    facts: list[str]


class AgentRememberRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    fact: str = Field(min_length=2, max_length=500)
    kind: Literal["fact", "preference", "entity"] = "fact"


class SupervisorRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    session_id: str = Field(default="default", min_length=1, max_length=100)
    file_path: str | None = Field(default=None, max_length=200)


class WorkerHandoff(BaseModel):
    worker: str
    summary: str
    details: dict


class SupervisorResponse(BaseModel):
    query: str
    route: list[str]
    answer: str
    handoffs: list[WorkerHandoff]
    traces: list[dict]


class MultiHopRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    session_id: str = Field(default="multi-hop", min_length=1, max_length=100)


class MultiHopResponse(BaseModel):
    question: str
    steps: list[str]
    answer: str
    session_id: str
    traces: list[dict]


class TraceListResponse(BaseModel):
    events: list[dict]
