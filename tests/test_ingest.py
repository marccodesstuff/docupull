from pathlib import Path

import pytest


def test_accept_pdf_requires_pdf_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUPULL_UPLOAD_DIR", str(tmp_path))
    t = tmp_path / "x.txt"
    t.write_text("hi")
    from core.ingest import accept_pdf
    with pytest.raises(ValueError):
        accept_pdf(t)


def test_accept_pdf_relative_goes_under_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUPULL_UPLOAD_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "f.pdf").write_text("hi")
    from core.ingest import accept_pdf
    out = accept_pdf("f.pdf")
    assert out.resolve() == (tmp_path / "f.pdf").resolve()


def test_accept_pdf_missing_raises():
    from core.ingest import accept_pdf
    with pytest.raises(FileNotFoundError):
        accept_pdf("no.pdf")
