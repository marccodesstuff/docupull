from __future__ import annotations

import pytest

from core.schema.lab_report import LabReport
from core.validate import coerce_field, validate_document


def test_validate_document_coerces_report_date() -> None:
    data = LabReport(patient_id="P1", report_date="2026-07-08")
    out = validate_document(data=data, schema=LabReport)
    assert out.report_date == "2026-07-08"


def test_validate_document_rejects_missing_required() -> None:
    data = LabReport(patient_id="P1", report_date="2026-07-08")
    data = data.model_copy(update={"patient_id": None})
    with pytest.raises(ValueError):
        validate_document(data=data, schema=LabReport)


def test_coerce_field_preserves_valid_text() -> None:
    value, ok = coerce_field("ordering_provider", "Dr. Smith", LabReport)
    assert ok is True
    assert value == "Dr. Smith"
