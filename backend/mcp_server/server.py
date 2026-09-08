"""
NotesLab MCP server.

Exposes:
- Resource: noteslab://app/overview (app context)
- Tool: search_notes (query local notes.db)

Run (stdio — for Cursor / Claude Code):
  cd backend && .venv/bin/python -m mcp_server.server

Or use the custom client:
  cd backend && .venv/bin/python -m mcp_server.client
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "notes.db"

mcp = MCPServer(
    "noteslab",
    instructions=(
        "NotesLab MCP server for the Arbisoft internship app. "
        "Use the overview resource for project context and search_notes to query saved notes."
    ),
)


@mcp.resource("noteslab://app/overview")
def app_overview() -> str:
    """One app resource: project overview for MCP clients."""
    return (
        "NotesLab is a FastAPI + React notes application with JWT auth, "
        "a SerpAPI research agent, supervisor/worker orchestration, and tool-call tracing. "
        f"SQLite database path: {DB_PATH}"
    )


@mcp.tool()
def search_notes(query: str, limit: int = 5) -> str:
    """Search NotesLab notes by title/content substring (local SQLite)."""
    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20")
    if not DB_PATH.exists():
        return (
            "notes.db not found. Start the FastAPI backend once so the database is created, "
            "then retry search_notes."
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, title, content
            FROM notes
            WHERE lower(title) LIKE ? OR lower(content) LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (f"%{query.lower()}%", f"%{query.lower()}%", limit),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return f"No notes matched query: {query!r}"

    lines = [f"Found {len(rows)} note(s) for {query!r}:"]
    for note_id, title, content in rows:
        lines.append(f"- [{note_id}] {title}: {content[:160]}")
    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
