from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image


def _write_png(path: Path, arr: np.ndarray) -> None:
    Image.fromarray(arr).save(path)


def test_preprocess_returns_path(tmp_path: Path) -> None:
    img = np.zeros((64, 64), dtype=np.uint8)
    img[10:54, 10:54] = 255
    src = tmp_path / "page.png"
    _write_png(src, img)
    out = __import__("core.preprocess", fromlist=["preprocess_image"]).preprocess_image(str(src))
    assert Path(out).exists()


def test_preprocess_raises_on_missing() -> None:
    with pytest.raises(FileNotFoundError):
        __import__("core.preprocess", fromlist=["preprocess_image"]).preprocess_image(
            str(Path("c:/missing.png"))
        )


def test_preprocess_output_is_binary_like(tmp_path: Path) -> None:
    img = np.zeros((32, 32), dtype=np.uint8)
    img[:, :] = 30
    src = tmp_path / "page.png"
    _write_png(src, img)
    out = __import__("core.preprocess", fromlist=["preprocess_image"]).preprocess_image(str(src))
    arr = np.array(Image.open(out))
    assert set(np.unique(arr)).issubset({0, 255})
