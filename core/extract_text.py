from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz


def render_text(path: Path | str) -> list[dict[str, Any]]:
    """Return per-page fitz-extracted text metadata for later classification."""
    doc = fitz.open(str(path))
    pages: list[dict[str, Any]] = []
    for idx in range(doc.page_count):
        page = doc.load_page(idx)
        text = page.get_text()
        pages.append({"index": idx, "text": text, "chars": len(text)})
    return pages


def extract_tables(path: Path | str) -> list[dict[str, Any]]:
    raise NotImplementedError("Tables extraction in Phase 1")
