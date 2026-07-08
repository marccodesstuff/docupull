"""Per-field confidence scoring for extracted document fields."""

from __future__ import annotations

from typing import Any

from core.schema.lab_report import LabReport


def _source_conf(*, kind: str, ocr_mean_conf: float | None) -> float:
    if kind == "digital":
        return 1.0
    if ocr_mean_conf is not None:
        return max(0.0, min(1.0, ocr_mean_conf))
    return 0.5


def _cross_check(name: str, value: Any) -> float:
    if name == "report_date" and isinstance(value, str):
        return 1.0 if len(value) == 10 else 0.7
    if name == "patient_id" and isinstance(value, str):
        return 1.0 if len(value) >= 4 else 0.7
    return 1.0


def _validation_bonus(value: Any) -> float:
    return 1.0 if value is not None and value != "" else 0.5


def score_field(*, name: str, value: Any, kind: str, ocr_mean_conf: float | None = None) -> float:
    source = _source_conf(kind=kind, ocr_mean_conf=ocr_mean_conf)
    cross = _cross_check(name=name, value=value)
    validation = _validation_bonus(value)
    return max(0.0, min(1.0, source * cross * validation))


def route_document(*, scores: dict[str, float], threshold: float = 0.75, required: list[str] | None = None) -> str:
    required = required or list(LabReport.model_fields.keys())
    for field in required:
        if scores.get(field, 0.0) < threshold:
            return "needs_review"
    return "ok"


class FieldScore:
    __slots__ = ("name", "confidence", "source", "value")

    def __init__(self, name: str, confidence: float, source: str, value: Any) -> None:
        self.name = name
        self.confidence = confidence
        self.source = source
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "confidence": self.confidence, "source": self.source, "value": self.value}
