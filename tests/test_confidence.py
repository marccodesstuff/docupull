from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from core.confidence import route_document
from core.confidence import score_field
from core.pipeline import run
from core.schema.lab_report import LabReport


def test_score_field_digital_is_high() -> None:
    score = score_field(name="patient_id", value="ABCD", kind="digital")
    assert score == 1.0


def test_score_field_scanned_uses_ocr_mean() -> None:
    score = score_field(name="patient_id", value="ABCD", kind="scanned", ocr_mean_conf=0.8)
    assert score == pytest.approx(0.8, abs=0.01)


def test_route_document_needs_review_when_low_score() -> None:
    scores = {
        "patient_id": 0.9,
        "report_date": 0.9,
        "ordering_provider": 0.9,
        "panel": 0.5,
    }
    assert route_document(scores=scores) == "needs_review"


def test_route_document_ok_when_above_threshold() -> None:
    scores = {
        "patient_id": 0.9,
        "report_date": 0.9,
        "ordering_provider": 0.9,
        "panel": 0.9,
    }
    assert route_document(scores=scores) == "ok"


def test_run_returns_expected_keys(tmp_path) -> None:

    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 72 72]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF\n"
    )
    fake_data = LabReport(patient_id="P1", report_date="2026-07-08")
    fake_client = MagicMock()
    fake_client.generate_structured.return_value = fake_data

    class FakeKind:
        value = "digital"

    class FakeClass:
        kind = FakeKind()

    fake_field = MagicMock()
    fake_field.to_dict.return_value = {"name": "patient_id", "confidence": 0.9, "source": "text", "value": "P1"}

    with patch("core.pipeline.extract_structured", return_value=fake_data), \
         patch("core.pipeline.validate_document", return_value=fake_data), \
         patch("core.pipeline.score_field", return_value=0.9), \
         patch("core.pipeline.FieldScore", return_value=fake_field), \
         patch("core.pipeline.route_document", return_value="ok"), \
         patch("core.pipeline._page_densities", return_value=[(0, 500)]), \
         patch("core.pipeline.classify_pages", return_value=[FakeClass()]), \
         patch("core.pipeline.render_text", return_value=[{"index": 0, "text": "x", "chars": 500}]), \
         patch("core.extract_structured.build_client", return_value=fake_client):
        result = run(str(pdf))
    assert {"schema", "scores", "overall_status", "source"} <= result.keys()
