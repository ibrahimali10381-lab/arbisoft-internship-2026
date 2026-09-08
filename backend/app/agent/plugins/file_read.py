"""File-read plugin: agent can read .txt / .pdf files under a safe root."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.agent.hooks import traced_tool

# file: backend/app/agent/plugins/file_read.py
# parents[3] = backend/, parents[4] = repo root
REPO_ROOT = Path(__file__).resolve().parents[4]
ALLOWED_ROOT = (REPO_ROOT / "sample_docs").resolve()


class FileReadPlugin:
    name = "file_read"
    description = "Read text from an allowed .txt or .pdf file under sample_docs/."

    @traced_tool(agent="file_worker", tool="file_read")
    def read(self, relative_path: str, *, max_chars: int = 4000) -> str:
        candidate = (ALLOWED_ROOT / relative_path).resolve()
        if not str(candidate).startswith(str(ALLOWED_ROOT)):
            raise ValueError("Path escapes the allowed sample_docs directory")
        if not candidate.exists() or not candidate.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")

        suffix = candidate.suffix.lower()
        if suffix == ".txt":
            text = candidate.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            reader = PdfReader(str(candidate))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            raise ValueError("Only .txt and .pdf files are supported")

        text = text.strip()
        if len(text) > max_chars:
            return text[:max_chars] + "\n…[truncated]"
        return text


file_read_plugin = FileReadPlugin()
