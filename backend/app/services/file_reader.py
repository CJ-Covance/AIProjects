from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import List


SUPPORTED_EXTENSIONS = {".pdf", ".html", ".htm", ".md", ".txt"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self._parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self._parts)


def extract_html_text(file_path: Path) -> str:
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.get_text()
    if not text.strip():
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_pdf_text(file_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError(
            "PDF support requires pypdf. Install with: pip install pypdf"
        ) from exc
    reader = PdfReader(str(file_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages).strip()


def read_file_content(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(file_path)
    if suffix in {".html", ".htm"}:
        return extract_html_text(file_path)
    if suffix in {".md", ".txt"}:
        return file_path.read_text(encoding="utf-8", errors="ignore").strip()
    raise ValueError(f"Unsupported file type: {suffix}")


def list_supported_files(folder: Path) -> List[Path]:
    if not folder.exists() or not folder.is_dir():
        return []
    files: List[Path] = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return files
