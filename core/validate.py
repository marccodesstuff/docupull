"""Validation and coercion helpers for extracted document data."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ValidationError

from core.schema.lab_report import AnalyteResult


def _try_parse_date(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def coerce_field(name: str, value: object, schema: type[BaseModel]) -> tuple[object, bool]:
    if name == "report_date":
        parsed = _try_parse_date(value)
        return parsed, parsed is not None

    if name == "panel":
        if not isinstance(value, list):
            return value, False
        coerced: list[AnalyteResult] = []
        valid = True
        for item in value:
            if isinstance(item, AnalyteResult):
                coerced.append(item)
                continue
            if isinstance(item, dict):
                try:
                    coerced.append(AnalyteResult.model_validate(item))
                except ValidationError:
                    valid = False
            else:
                valid = False
        return coerced, valid

    return value, True


def validate_document(*, data: BaseModel, schema: type[BaseModel]) -> BaseModel:
    """Recoerce known fields into their target types when possible."""
    source = data.model_dump()
    for name, value in list(source.items()):
        coerced, ok = coerce_field(name, value, schema)
        if ok:
            source[name] = coerced
    try:
        return schema.model_validate(source)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
