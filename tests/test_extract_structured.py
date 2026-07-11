from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from core.extract_structured import build_prompt
from core.extract_structured import extract_structured
from core.schema.lab_report import LabReport


def test_build_prompt_includes_schema_fields() -> None:
    prompt = build_prompt(text="hello", schema=LabReport)
    assert "patient_id" in prompt
    assert "report_date" in prompt
    assert "panel" in prompt


def test_extract_structured_uses_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.generate_structured.return_value = LabReport(
        patient_id="P1", report_date="2026-07-08"
    )
    monkeypatch.setattr("core.extract_structured.build_client", lambda: fake_client)
    out = extract_structured(text="some text", schema=LabReport)
    assert out.patient_id == "P1"
    fake_client.generate_structured.assert_called_once()


def test_extract_structured_defaults_to_lab_report(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.generate_structured.return_value = LabReport(
        patient_id="P1", report_date="2026-07-08"
    )
    monkeypatch.setattr("core.extract_structured.build_client", lambda: fake_client)
    out = extract_structured(text="some text")
    assert isinstance(out, LabReport)
