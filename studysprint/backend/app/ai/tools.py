"""Agent tools. Each is registered so agents and routes call it through the traced registry."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.outputs import (
    AnswerOutput,
    GradeOutput,
    QuestionsOutput,
    TopicsOutput,
    grade_guard,
    pages_guard,
)
from app.ai.registry import registry
from app.ai.router import router
from app.models import Attempt, Chunk, Course, Document, Question, Topic, User
from app.services import scheduler
from app.services.ingest import chunk_text, extract_pages
from app.services.retrieval import retrieve


def _course_pages(db: Session, course_id: int) -> set[int]:
    return set(db.scalars(select(Chunk.page).where(Chunk.course_id == course_id)))


@registry.tool("extract_topics", "Split uploaded pages into study topics with source pages.")
def extract_topics(
    db: Session, course: Course, document: Document, pages: list[tuple[int, str]]
) -> dict:
    payload = {
        "pages": [{"page": n, "text": text[:3000]} for n, text in pages[:40]],
        "max_topics": 12,
    }
    result = router.run("extract_topics", payload, TopicsOutput, pages_guard({n for n, _ in pages}))
    existing = {t.name.lower() for t in course.topics}
    created = 0
    for item in result.output.topics:
        if item.name.lower() in existing:
            continue
        existing.add(item.name.lower())
        db.add(
            Topic(
                course_id=course.id,
                document_id=document.id,
                name=item.name,
                summary=item.summary,
                source_page=item.source_page,
            )
        )
        created += 1
    db.flush()
    return {"topics_created": created, "model": result.model}


@registry.tool("ingest_document", "Extract text from a PDF/TXT, chunk it and extract topics.")
def ingest_document(db: Session, course: Course, filename: str, data: bytes) -> dict:
    pages = extract_pages(data, filename)
    document = Document(course_id=course.id, filename=filename, page_count=len(pages))
    db.add(document)
    db.flush()
    for page, text in pages:
        for piece in chunk_text(text):
            db.add(Chunk(document_id=document.id, course_id=course.id, page=page, text=piece))
    db.flush()
    result = registry.call("extract_topics", db=db, course=course, document=document, pages=pages)
    db.commit()
    db.refresh(document)
    return {"document": document, **result}


@registry.tool("generate_questions", "Write page-cited open questions for one topic.")
def generate_questions(db: Session, topic: Topic, count: int = 3) -> dict:
    passages = retrieve(
        db, topic.course_id, f"{topic.name}. {topic.summary}", k=4, page=topic.source_page
    )
    if not passages:
        return {"created": 0, "model": "none"}
    passages = [p for p in passages if p["page"] == topic.source_page] or passages
    payload = {
        "topic": topic.name,
        "count": count,
        "passages": [{"page": p["page"], "text": p["text"]} for p in passages],
    }
    result = router.run(
        "generate_questions",
        payload,
        QuestionsOutput,
        pages_guard(_course_pages(db, topic.course_id)),
    )
    existing = {q.prompt.lower() for q in topic.questions}
    created = 0
    for item in result.output.questions:
        if item.prompt.lower() in existing:
            continue
        existing.add(item.prompt.lower())
        db.add(
            Question(
                topic_id=topic.id,
                prompt=item.prompt,
                reference_answer=item.reference_answer,
                key_points=item.key_points,
                source_page=item.source_page,
                model=result.model,
            )
        )
        created += 1
    db.commit()
    db.refresh(topic)
    return {"created": created, "model": result.model}


@registry.tool("update_mastery", "Blend a new 0-5 score into a topic's mastery.")
def update_mastery(topic: Topic, score: int) -> dict:
    topic.mastery = scheduler.updated_mastery(topic.mastery, topic.attempts, score)
    topic.attempts += 1
    topic.last_practiced_at = datetime.now(UTC)
    return {"topic_id": topic.id, "mastery": topic.mastery}


@registry.tool("grade_answer", "Score a free-text answer against the source and update mastery.")
def grade_answer(
    db: Session, question: Question, user: User, answer: str, model: str | None = None
) -> Attempt:
    payload = {
        "question": question.prompt,
        "reference_answer": question.reference_answer,
        "key_points": question.key_points,
        "source_page": question.source_page,
        "answer": answer,
    }
    result = router.run(
        "grade_answer", payload, GradeOutput, grade_guard(question.key_points), model=model
    )
    grade = result.output
    assert isinstance(grade, GradeOutput)
    attempt = Attempt(
        question_id=question.id,
        user_id=user.id,
        answer=answer,
        score=grade.score,
        feedback=grade.feedback,
        missing_points=grade.missing_points,
        model=result.model,
    )
    db.add(attempt)
    registry.call("update_mastery", topic=question.topic, score=grade.score)
    db.commit()
    db.refresh(attempt)
    return attempt


def _topic_states(course: Course) -> list[scheduler.TopicState]:
    return [
        scheduler.TopicState(
            id=t.id,
            name=t.name,
            mastery=t.mastery,
            attempts=t.attempts,
            last_practiced=t.last_practiced_at.date() if t.last_practiced_at else None,
        )
        for t in course.topics
    ]


@registry.tool("plan_sessions", "Build a day-by-day practice plan up to the exam date.")
def plan_sessions(course: Course, per_day: int = 3) -> list[dict]:
    return scheduler.build_plan(
        _topic_states(course), scheduler.today_utc(), course.exam_date, per_day
    )


@registry.tool("build_session", "Pick today's questions, weakest topics first.")
def build_session(db: Session, course: Course, user: User, size: int = 5) -> list[Question]:
    by_id = {t.id: t for t in course.topics}
    ranked = [by_id[s.id] for s in scheduler.rank(_topic_states(course), scheduler.today_utc())]
    picked: list[Question] = []
    for topic in ranked[:size]:
        if not topic.questions:
            registry.call("generate_questions", db=db, topic=topic, count=3)
    last_attempt = dict(
        db.execute(
            select(Attempt.question_id, func.max(Attempt.created_at))
            .where(Attempt.user_id == user.id)
            .group_by(Attempt.question_id)
        ).all()
    )
    pools = {
        t.id: sorted(
            t.questions, key=lambda q: (last_attempt.get(q.id) is not None, last_attempt.get(q.id))
        )
        for t in ranked[:size]
    }
    while len(picked) < size and any(pools.values()):
        for topic in ranked[:size]:
            if pools[topic.id] and len(picked) < size:
                picked.append(pools[topic.id].pop(0))
    return picked


@registry.tool("answer_question", "Answer a question from the course material with citations.")
def answer_question(db: Session, course: Course, question: str, model: str | None = None) -> dict:
    passages = retrieve(db, course.id, question, k=5)
    if not passages:
        return {
            "answer": "Upload course material first — I only answer from your documents.",
            "citations": [],
            "model": "none",
            "cached": False,
        }
    payload = {
        "question": question,
        "passages": [{"page": p["page"], "text": p["text"]} for p in passages],
    }
    result = router.run(
        "answer_question",
        payload,
        AnswerOutput,
        pages_guard({p["page"] for p in passages}),
        model=model,
    )
    output = result.output
    assert isinstance(output, AnswerOutput)
    by_page = {p["page"]: p for p in passages}
    citations = [
        {
            "page": page,
            "document": by_page[page]["document"],
            "excerpt": by_page[page]["text"][:240],
        }
        for page in output.citations
        if page in by_page
    ]
    return {
        "answer": output.answer,
        "citations": citations,
        "model": result.model,
        "cached": result.cached,
    }
