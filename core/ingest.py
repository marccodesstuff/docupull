from __future__ import annotations

from pathlib import Path

import os


def accept_pdf(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    if p.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF: {p}")

    if p.is_absolute():
        return p.resolve()

    root = Path(os.environ.get("DOCUPULL_UPLOAD_DIR", "./tmp/uploads")).resolve()
    return (root / p).resolve()
