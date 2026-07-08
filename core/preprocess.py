from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def preprocess_image(image_path: str) -> str:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(image_path)

    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 15
    )

    coords = np.column_stack(np.where(binary == 0))
    angle = 0.0
    if coords.size:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        angle = 90 - angle if angle > 45 else -angle
        h, w = binary.shape
        m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        binary = cv2.warpAffine(binary, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    out_path = image_path + ".preprocessed.png"
    Image.fromarray(binary).save(out_path)
    return out_path
