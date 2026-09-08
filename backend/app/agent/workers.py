"""Worker agents used by the supervisor."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agent import research_agent
from app.agent.hooks import traced_tool
from app.agent.plugins.file_read import file_read_plugin
from app.models import Note


@dataclass
class WorkerResult:
    worker: str
    summary: str
    details: dict


class ResearchWorker:
    name = "research_worker"

    @traced_tool(agent="research_worker", tool="serp_research")
    def run(self, query: str, session_id: str) -> WorkerResult:
        result = research_agent.run(query=query, session_id=session_id)
        return WorkerResult(
            worker=self.name,
            summary=result.answer,
            details={
                "plan": result.plan,
                "sources": [
                    {"title": s.title, "link": s.link, "snippet": s.snippet} for s in result.sources
                ],
                "memory_used": result.memory_used,
            },
        )


class NotesWorker:
    name = "notes_worker"

    @traced_tool(agent="notes_worker", tool="search_notes")
    def run(self, query: str, db: Session, owner_id: int | None = None) -> WorkerResult:
        q = db.query(Note)
        if owner_id is not None:
            q = q.filter(Note.owner_id == owner_id)
        notes = q.order_by(Note.id.desc()).limit(50).all()
        needle = query.lower()
        matches = [
            note for note in notes if needle in note.title.lower() or needle in note.content.lower()
        ]
        if not matches:
            summary = f"No notes matched “{query}”."
        else:
            lines = [f"Found {len(matches)} note(s) for “{query}”:"]
            for note in matches[:5]:
                lines.append(f"- [{note.id}] {note.title}: {note.content[:120]}")
            summary = "\n".join(lines)

        return WorkerResult(
            worker=self.name,
            summary=summary,
            details={
                "match_count": len(matches),
                "note_ids": [n.id for n in matches[:10]],
            },
        )


class FileWorker:
    name = "file_worker"

    @traced_tool(agent="file_worker", tool="read_document")
    def run(self, relative_path: str) -> WorkerResult:
        text = file_read_plugin.read(relative_path)
        return WorkerResult(
            worker=self.name,
            summary=f"Read {relative_path} ({len(text)} chars).",
            details={"path": relative_path, "content": text},
        )


research_worker = ResearchWorker()
notes_worker = NotesWorker()
file_worker = FileWorker()
