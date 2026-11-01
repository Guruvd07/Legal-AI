
from pathlib import Path

import fitz

from app.services.ocr_service import extract_text_from_pdf_page


def extract_pdf_text(file_path: str) -> dict:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError("PDF file not found")

    pages = []

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            extraction_method = "native"

            # Use OCR for scanned pages or pages with very little text.
            if len(text) < 40:
                ocr_text = extract_text_from_pdf_page(page)

                if len(ocr_text) > len(text):
                    text = ocr_text
                    extraction_method = "ocr"

            pages.append({
                "page_number": page_number,
                "text": text,
                "character_count": len(text),
                "extraction_method": extraction_method,
            })

    return {
        "filename": path.name,
        "page_count": len(pages),
        "total_characters": sum(
            page["character_count"] for page in pages
        ),
        "pages": pages,
    }
