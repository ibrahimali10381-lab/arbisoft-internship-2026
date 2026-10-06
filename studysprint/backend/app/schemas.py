from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- auth ---


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(ORMModel):
    id: int
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# --- courses ---


class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    exam_date: date | None = None


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    exam_date: date | None = None


class TopicRead(ORMModel):
    id: int
    name: str
    summary: str
    source_page: int
    mastery: float
    attempts: int
    last_practiced_at: datetime | None
    question_count: int = 0


class DocumentRead(ORMModel):
    id: int
    filename: str
    page_count: int
    created_at: datetime


class CourseRead(ORMModel):
    id: int
    title: str
    exam_date: date | None
    created_at: datetime
    document_count: int = 0
    topic_count: int = 0
    average_mastery: float = 0.0


class CourseDetail(CourseRead):
    documents: list[DocumentRead]
    topics: list[TopicRead]


class UploadResponse(BaseModel):
    document: DocumentRead
    topics_created: int
    model: str


# --- study ---


class QuestionRead(ORMModel):
    id: int
    topic_id: int
    prompt: str
    source_page: int
    model: str


class QuestionWithAnswer(QuestionRead):
    reference_answer: str
    key_points: list[str]


class GenerateQuestionsRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=8)


class SessionQuestion(QuestionRead):
    topic_name: str
    topic_mastery: float


class SessionResponse(BaseModel):
    course_id: int
    questions: list[SessionQuestion]


class AttemptCreate(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)


class AttemptRead(ORMModel):
    id: int
    question_id: int
    score: int
    feedback: str
    missing_points: list[str]
    model: str
    created_at: datetime
    reference_answer: str
    source_page: int
    topic_mastery: float


class PlanTopic(BaseModel):
    id: int
    name: str
    mastery: float


class PlanDay(BaseModel):
    date: date
    focus: Literal["learn", "practice", "review"]
    topics: list[PlanTopic]


class PlanResponse(BaseModel):
    course_id: int
    exam_date: date | None
    days: list[PlanDay]


# --- AI ---


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    model: str | None = None


class Citation(BaseModel):
    page: int
    document: str
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    model: str
    cached: bool


class CompareRequest(BaseModel):
    task: Literal["ask", "grade"]
    course_id: int
    question: str | None = Field(default=None, max_length=500)
    question_id: int | None = None
    answer: str | None = Field(default=None, max_length=4000)
    models: list[str] | None = None


class CompareRow(BaseModel):
    model: str
    ok: bool
    latency_ms: float
    output: dict | None = None
    error: str | None = None


class CompareResponse(BaseModel):
    task: str
    rows: list[CompareRow]


class ModelInfo(BaseModel):
    id: str
    label: str
    kind: Literal["llm", "local"]
    available: bool


class AgentRunRequest(BaseModel):
    course_id: int
    goal: str = Field(min_length=3, max_length=500)


class AgentStep(BaseModel):
    worker: str
    tool: str
    summary: str


class AgentRunResponse(BaseModel):
    run_id: str
    intent: str
    steps: list[AgentStep]
    output: dict


class TraceEvent(BaseModel):
    id: str
    run_id: str | None
    kind: str
    name: str
    status: str
    duration_ms: float
    started_at: datetime
    detail: dict


class ToolInfo(BaseModel):
    name: str
    description: str
