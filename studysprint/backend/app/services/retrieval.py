from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import text as T
from app.models import Chunk, Document


def retrieve(
    db: Session, course_id: int, query: str, k: int = 4, page: int | None = None
) -> list[dict]:
    """TF-IDF retrieval over a course's chunks; chunks on `page` get a boost."""
    rows = db.execute(
        select(Chunk, Document.filename)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.course_id == course_id)
    ).all()
    if not rows:
        return []
    weights = T.idf(chunk.text for chunk, _ in rows)
    q_vec = T.vector(query, weights)
    scored = []
    for chunk, filename in rows:
        score = T.cosine(q_vec, T.vector(chunk.text, weights))
        if page is not None and chunk.page == page:
            score += 0.5
        scored.append((score, chunk, filename))
    scored.sort(key=lambda s: -s[0])
    return [
        {"page": c.page, "text": c.text, "document": f, "score": round(s, 4)}
        for s, c, f in scored[:k]
        if s > 0
    ]
