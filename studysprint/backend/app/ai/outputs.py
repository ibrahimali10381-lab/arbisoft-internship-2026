"""Structured outputs every model must return, plus semantic guards beyond the schema."""

from collections.abc import Callable

from pydantic import BaseModel, Field, field_validator


class GuardError(ValueError):
    pass


class TopicItem(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    summary: str = Field(default="", max_length=600)
    source_page: int = Field(ge=1)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip().rstrip(".:")


class TopicsOutput(BaseModel):
    topics: list[TopicItem] = Field(min_length=1, max_length=15)


class QuestionItem(BaseModel):
    prompt: str = Field(min_length=8, max_length=500)
    reference_answer: str = Field(min_length=3, max_length=1500)
    key_points: list[str] = Field(min_length=1, max_length=6)
    source_page: int = Field(ge=1)


class QuestionsOutput(BaseModel):
    questions: list[QuestionItem] = Field(min_length=1, max_length=10)


class GradeOutput(BaseModel):
    score: int = Field(ge=0, le=5)
    feedback: str = Field(min_length=1, max_length=1500)
    missing_points: list[str] = Field(default_factory=list, max_length=6)


class AnswerOutput(BaseModel):
    answer: str = Field(min_length=1, max_length=2500)
    citations: list[int] = Field(default_factory=list, max_length=6)


Guard = Callable[[BaseModel], None]


def pages_guard(valid_pages: set[int]) -> Guard:
    """Reject outputs that cite pages the student never uploaded."""

    def check(output: BaseModel) -> None:
        items = getattr(output, "topics", None) or getattr(output, "questions", None) or []
        bad = sorted({i.source_page for i in items if i.source_page not in valid_pages})
        cited = getattr(output, "citations", None) or []
        bad += sorted({p for p in cited if p not in valid_pages})
        if bad:
            raise GuardError(f"cites pages not in the material: {bad}")

    return check


def grade_guard(key_points: list[str]) -> Guard:
    def check(output: BaseModel) -> None:
        assert isinstance(output, GradeOutput)
        if output.score == 5 and output.missing_points:
            raise GuardError("score 5 cannot have missing points")
        if output.score == 0 and not output.missing_points and key_points:
            raise GuardError("score 0 must list missing points")

    return check
