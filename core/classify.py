from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PageKind(StrEnum):
    digital = "digital"
    scanned = "scanned"


@dataclass(frozen=True)
class PageClass:
    index: int
    kind: PageKind


def classify_pages(pages_text_chars: list[tuple[int, int]]) -> list[PageClass]:
    return [
        PageClass(index=idx, kind=PageKind.digital if chars >= 200 else PageKind.scanned)
        for idx, chars in pages_text_chars
    ]
