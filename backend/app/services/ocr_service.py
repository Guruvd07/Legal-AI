
import io
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image


# Windows Tesseract installation path
TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


def extract_text_from_image(image: Image.Image) -> str:
    """Preprocess a scanned page and extract text using Tesseract."""

    image_array = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Improve readability for many scanned documents.
    processed = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        processed,
        config="--oem 3 --psm 6",
    )

    return text.strip()


def extract_text_from_pdf_page(page) -> str:
    """Render one PyMuPDF page and run OCR on it."""

    pixmap = page.get_pixmap(dpi=250, alpha=False)
    image_bytes = pixmap.tobytes("png")

    with Image.open(io.BytesIO(image_bytes)) as image:
        return extract_text_from_image(image)
