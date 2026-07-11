"""End-to-end pipeline wiring: ingest -> classify -> extract -> validate -> score -> route."""

from __future__ import annotations

from typing import Any

from core.classify import PageKind
from core.classify import classify_pages
from core.confidence import FieldScore
from core.confidence import route_document
from core.confidence import score_field
from core.extract_structured import extract_structured
from core.extract_text import render_text
from core.ocr import ocr_page
from core.schema.lab_report import LabReport
from core.validate import validate_document


def _page_densities(path: str) -> list[tuple[int, int]]:
    pages = render_text(path)
    return [(p["index"], p["chars"]) for p in pages]


def _extract_text(path: str) -> str:
    pages = render_text(path)
    return "\n".join(p["text"] for p in pages)


def run(path: str, *, threshold: float = 0.75, tesseract_cmd: str | None = None) -> dict[str, Any]:
    densities = _page_densities(path)
    classes = classify_pages(densities)

    scanned = any(cls.kind == PageKind.scanned for cls in classes)
    if scanned:
        import os

        import fitz

        doc = fitz.open(path)
        page_texts: list[str] = []
        ocr_confs: list[float] = []
        for idx in range(doc.page_count):
            page = doc.load_page(idx)
            if classes[idx].kind == PageKind.digital:
                page_texts.append(page.get_text())
            else:
                pix = page.get_pixmap(dpi=300)
                img_path = os.path.splitext(path)[0] + f"_page_{idx}.png"
                pix.save(img_path)
                result = ocr_page(img_path, tesseract_cmd=tesseract_cmd)
                page_texts.append(result.text)
                if result.mean_confidence:
                    ocr_confs.append(result.mean_confidence)
                from contextlib import suppress

                with suppress(OSError):
                    os.remove(img_path)
        text = "\n".join(page_texts)
        ocr_mean = (sum(ocr_confs) / len(ocr_confs)) if ocr_confs else None
    else:
        text = _extract_text(path)
        ocr_mean = None

    raw = extract_structured(text=text, schema=LabReport)
    data = validate_document(data=raw, schema=LabReport)

    values = data.model_dump()
    scores: dict[str, float] = {}
    for name, value in values.items():
        kind = "scanned" if scanned else "digital"
        scores[name] = score_field(name=name, value=value, kind=kind, ocr_mean_conf=ocr_mean)

    status = route_document(scores=scores, threshold=threshold)
    fields = [FieldScore(name=name, confidence=scores[name], source=("ocr" if scanned else "text"), value=value).to_dict() for name, value in values.items()]
    return {"schema": data.model_dump(), "scores": fields, "overall_status": status, "source": "ocr" if scanned else "text"}
