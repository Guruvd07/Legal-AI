
import os
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from ultralytics import YOLO


MODEL_PATH = Path(
    os.getenv(
        "LEGALAI_LAYOUT_MODEL",
        r"C:\Users\sai\.cache\huggingface\hub\models--ashen007--document-structure-detection\snapshots\1ef1827b6b90d48f8f968b7e7ab91ec9dab07458\DSD-YOLOv8-v2.pt",
    )
)

LAYOUT_CLASSES = {"Table", "Figure"}


@lru_cache(maxsize=1)
def get_layout_model() -> YOLO:
    """Load the layout model once per backend process."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"YOLO layout model not found: {MODEL_PATH}"
        )

    return YOLO(str(MODEL_PATH))


def detect_document_layout(
    file_path: str,
    confidence_threshold: float = 0.25,
    image_scale: float = 2.0,
) -> dict:
    """
    Detect tables and figures in a PDF.

    Bounding boxes use pixel coordinates in each rendered page image.
    Page numbers are one-based.
    """
    pdf_path = Path(file_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("confidence_threshold must be between 0 and 1")

    if image_scale <= 0:
        raise ValueError("image_scale must be greater than 0")

    model = get_layout_model()
    detections = []

    with pymupdf.open(pdf_path) as pdf:
        page_count = len(pdf)
        for page_number, page in enumerate(pdf, start=1):
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(image_scale, image_scale),
                alpha=False,
            )

            image_bytes = pixmap.tobytes("png")
            image_array = cv2.imdecode(
                np.frombuffer(image_bytes, dtype=np.uint8),
                cv2.IMREAD_COLOR,
            )

            if image_array is None:
                raise ValueError(
                    f"Failed to render PDF page {page_number} as an image"
                )

            results = model.predict(
                source=image_array,
                conf=confidence_threshold,
                verbose=False,
            )
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]

                    if class_name not in LAYOUT_CLASSES:
                        continue

                    detections.append(
                        {
                            "page_number": page_number,
                            "label": class_name,
                            "confidence": round(float(box.conf[0]), 4),
                            "bbox": [
                                round(float(value), 2)
                                for value in box.xyxy[0].tolist()
                            ],
                            "coordinate_space": "rendered_page_pixels",
                            "image_width": pixmap.width,
                            "image_height": pixmap.height,
                        }
                    )

    return {
        "filename": pdf_path.name,
        "page_count": page_count,
        "model": MODEL_PATH.name,
        "confidence_threshold": confidence_threshold,
        "detection_count": len(detections),
        "detections": detections,
    }
