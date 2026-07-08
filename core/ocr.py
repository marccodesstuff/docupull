from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OCRPageResult:
    text: str
    mean_confidence: float
    words: list[dict[str, object]]


def ocr_page(image_path: str, *, tesseract_cmd: str | None = None) -> OCRPageResult:
    import os

    import pytesseract
    from PIL import Image

    if tesseract_cmd:
        os.environ.setdefault("TESSDATA_PREFIX", tesseract_cmd)

    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    words: list[dict[str, object]] = []
    confs: list[int] = []
    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        conf = int(data["conf"][i])
        if txt and conf > 0:
            words.append({"text": txt, "confidence": conf / 100.0})
            confs.append(conf)

    text = " ".join(w["text"] for w in words)
    mean_confidence = float(sum(confs) / len(confs)) / 100.0 if confs else 0.0
    return OCRPageResult(text=text, mean_confidence=mean_confidence, words=words)
