import os
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pymupdf


# ============================================================
# YOLO MODEL CONFIGURATION
# ============================================================

MODEL_REPO_ID = "ashen007/document-structure-detection"
MODEL_FILENAME = "DSD-YOLOv8-v2.pt"

# Optional custom model path through environment variable
CUSTOM_MODEL_PATH = os.getenv("LEGALAI_LAYOUT_MODEL")

LAYOUT_CLASSES = {"Table", "Figure"}


# ============================================================
# MODEL PATH RESOLUTION
# ============================================================

def resolve_model_path() -> Path:
    """
    Resolve the YOLO model path.

    If LEGALAI_LAYOUT_MODEL is configured, use that path.
    Otherwise, download or retrieve the model from Hugging Face cache.
    """

    if CUSTOM_MODEL_PATH:
        model_path = Path(CUSTOM_MODEL_PATH).expanduser()

        if not model_path.is_file():
            raise FileNotFoundError(
                f"YOLO layout model not found: {model_path}"
            )

        return model_path

    from huggingface_hub import hf_hub_download

    downloaded_path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME
    )

    return Path(downloaded_path)


# ============================================================
# LAZY YOLO MODEL LOADING
# ============================================================

@lru_cache(maxsize=1)
def get_layout_model():
    """
    Load YOLO only when layout detection is requested.
    Cache the loaded model to avoid repeated loading.
    """

    from ultralytics import YOLO

    model_path = resolve_model_path()

    if not model_path.is_file():
        raise FileNotFoundError(
            f"YOLO layout model not found: {model_path}"
        )

    return YOLO(str(model_path))


# ============================================================
# DOCUMENT LAYOUT DETECTION
# ============================================================

def detect_document_layout(
    file_path: str,
    confidence_threshold: float = 0.25,
    image_scale: float = 2.0
) -> dict:
    """
    Detect tables and figures in a PDF.

    Bounding boxes use pixel coordinates in each rendered page image.
    Page numbers are one-based.
    """

    pdf_path = Path(file_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError(
            "confidence_threshold must be between 0 and 1"
        )

    if image_scale <= 0:
        raise ValueError(
            "image_scale must be greater than 0"
        )

    model = get_layout_model()

    detections = []

    with pymupdf.open(pdf_path) as pdf:

        page_count = len(pdf)

        for page_number, page in enumerate(pdf, start=1):

            # Render PDF page into an image
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(
                    image_scale,
                    image_scale
                ),
                alpha=False
            )

            image_bytes = pixmap.tobytes("png")

            image_array = cv2.imdecode(
                np.frombuffer(
                    image_bytes,
                    dtype=np.uint8
                ),
                cv2.IMREAD_COLOR
            )

            if image_array is None:
                raise ValueError(
                    f"Failed to render PDF page {page_number} as an image"
                )

            # YOLO prediction
            results = model.predict(
                source=image_array,
                conf=confidence_threshold,
                verbose=False
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
                            "confidence": round(
                                float(box.conf[0]),
                                4
                            ),
                            "bbox": [
                                round(float(value), 2)
                                for value in box.xyxy[0].tolist()
                            ],
                            "coordinate_space": "rendered_page_pixels",
                            "image_width": pixmap.width,
                            "image_height": pixmap.height
                        }
                    )

    return {
        "filename": pdf_path.name,
        "page_count": page_count,
        "model": MODEL_FILENAME,
        "confidence_threshold": confidence_threshold,
        "detection_count": len(detections),
        "detections": detections
    }