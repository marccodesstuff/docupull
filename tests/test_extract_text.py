from pathlib import Path

import fitz
import pytest


def test_render_text_returns_index_chars_text(tmp_path):
    doc = fitz.open()
    page = doc.new_page(width=72, height=72)
    page.insert_text((0, 10), "Hello world")
    pdf_path = tmp_path / "sample.pdf"
    doc.save(str(pdf_path))
    doc.close()

    from core.extract_text import render_text

    pages = render_text(pdf_path)
    assert len(pages) == 1
    assert pages[0]["index"] == 0
    assert "Hello world" in pages[0]["text"]
    assert isinstance(pages[0]["chars"], int)


def test_extract_tables_not_implemented_yet(tmp_path):
    with pytest.raises(NotImplementedError):
        from core.extract_text import extract_tables

        extract_tables(tmp_path / "x.pdf")


def test_render_text_returns_empty_pages_for_blank_pdf(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page(width=72, height=72)
    doc.save(str(pdf_path))
    doc.close()

    from core.extract_text import render_text

    pages = render_text(pdf_path)
    assert len(pages) == 1
    assert pages[0]["chars"] == 0