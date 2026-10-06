import io
import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_PAGES = 200


class IngestError(ValueError):
    pass


def extract_pages(data: bytes, filename: str) -> list[tuple[int, str]]:
    """Return (page_number, text) pairs. Text files are split into pseudo-pages by heading."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise IngestError(f"Unsupported file type {ext or '(none)'}; upload PDF, TXT or MD")
    if not data:
        raise IngestError("File is empty")
    pages = _pdf_pages(data) if ext == ".pdf" else _text_pages(data)
    pages = [(n, t.strip()) for n, t in pages if t.strip()]
    if not pages:
        raise IngestError("No extractable text found (scanned PDFs are not supported)")
    return pages[:MAX_PAGES]


def _pdf_pages(data: bytes) -> list[tuple[int, str]]:
    if not data.startswith(b"%PDF"):
        raise IngestError("File is not a valid PDF")
    try:
        reader = PdfReader(io.BytesIO(data))
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    except (PdfReadError, ValueError, KeyError) as exc:
        raise IngestError(f"Could not read PDF: {exc}") from exc


def _text_pages(data: bytes) -> list[tuple[int, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestError("Text files must be UTF-8") from exc
    if "\f" in text:
        sections = text.split("\f")
    elif re.search(r"^#{1,3} ", text, re.MULTILINE):
        sections = re.split(r"^(?=#{1,3} )", text, flags=re.MULTILINE)
        sections = [re.sub(r"^#{1,3} ", "", s, count=1) for s in sections]
    else:
        sections = [text[i : i + 2500] for i in range(0, len(text), 2500)]
    return [(i + 1, s) for i, s in enumerate(s for s in sections if s.strip())]


def chunk_text(text: str, size: int = 900) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()] or [text]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) > size:
            chunks.append(current)
            current = ""
        current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks
