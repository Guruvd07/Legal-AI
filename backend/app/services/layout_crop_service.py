
import json
from pathlib import Path

import pymupdf
from PIL import Image


UPLOAD_DIR = Path("data/uploads")
DETECTIONS_DIR = Path("data/layout_detections")
CROPS_DIR = Path("data/layout_crops")


def crop_document_layout(document_id: str) -> dict:
    pdf_path = UPLOAD_DIR / f"{document_id}.pdf"
    detections_path = DETECTIONS_DIR / f"{document_id}.json"

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not detections_path.is_file():
        raise FileNotFoundError(
            f"Layout detections not found: {detections_path}"
        )

    with detections_path.open("r", encoding="utf-8") as file:
        layout_data = json.load(file)

    document_output_dir = CROPS_DIR / document_id
    document_output_dir.mkdir(parents=True, exist_ok=True)

    saved_crops = []

    with pymupdf.open(pdf_path) as pdf:
        for index, detection in enumerate(
            layout_data.get("detections", []), start=1
        ):
            page_number = detection["page_number"]

            if not 1 <= page_number <= len(pdf):
                continue

            page = pdf[page_number - 1]

            # Convert YOLO rendered-image pixel coordinates
            # back to PDF page coordinates.
            image_width = detection["image_width"]
            image_height = detection["image_height"]

            scale_x = page.rect.width / image_width
            scale_y = page.rect.height / image_height

            x1, y1, x2, y2 = detection["bbox"]

            clip = pymupdf.Rect(
                x1 * scale_x,
                y1 * scale_y,
                x2 * scale_x,
                y2 * scale_y,
            ) & page.rect

            if clip.is_empty or clip.is_infinite:
                continue

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                clip=clip,
                alpha=False,
            )

            output_name = (
                f"page_{page_number}_{detection['label'].lower()}_{index}.png"
            )
            output_path = document_output_dir / output_name
            pixmap.save(str(output_path))

            saved_crops.append(
                {
                    "page_number": page_number,
                    "label": detection["label"],
                    "confidence": detection["confidence"],
                    "image_path": str(output_path),
                    "width": pixmap.width,
                    "height": pixmap.height,
                }
            )

    return {
        "document_id": document_id,
        "crop_count": len(saved_crops),
        "crops": saved_crops,
    }
