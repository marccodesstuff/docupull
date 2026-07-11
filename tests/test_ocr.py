from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image


def _write_png(path: Path, arr: np.ndarray) -> None:
    Image.fromarray(arr).save(path)


def test_ocr_page_returns_text_and_confidence(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "page.png"
    _write_png(src, np.full((64, 64), 255, dtype=np.uint8))

    class _FakeData:
        text = ["Hello"]
        conf = [95]

    class FakeTess:
        def image_to_data(self, img, output_type):
            return {"text": ["Hello"], "conf": [95]}

    monkeypatch.setattr("pytesseract.image_to_data", FakeTess().image_to_data, raising=False)

    mod = __import__("core.ocr", fromlist=["ocr_page"])
    result = mod.ocr_page(str(src))
    assert result.text == "Hello"
    assert result.mean_confidence == pytest.approx(0.95)


def test_ocr_page_missing_input() -> None:
    mod = __import__("core.ocr", fromlist=["ocr_page"])
    with pytest.raises(FileNotFoundError):
        mod.ocr_page("C:/missing.png")
