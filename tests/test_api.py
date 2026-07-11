from __future__ import annotations

import pytest
from app.main import create_app
from core.schema.lab_report import LabReport
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_extract_rejects_non_pdf(client, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCUPULL_UPLOAD_DIR", "/tmp/nope")
    response = client.post("/extract", files={"file": ("doc.txt", b"hi", "text/plain")})
    assert response.status_code == 400


def test_extract_returns_json(client, monkeypatch: pytest.MonkeyPatch):
    pdf_bytes = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 72 72]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF\n"
    )
    fake_data = LabReport(patient_id="P1", report_date="2026-01-01")

    def fake_run(path):
        return {
            "schema": fake_data.model_dump(),
            "scores": [],
            "overall_status": "ok",
            "source": "text",
        }

    monkeypatch.setattr("app.routes.run", fake_run)
    response = client.post("/extract", files={"file": ("lab.pdf", pdf_bytes, "application/pdf")})
    assert response.status_code == 200
    assert response.json()["overall_status"] == "ok"
    assert response.json()["source"] == "text"
