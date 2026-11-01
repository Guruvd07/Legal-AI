import json
from pathlib import Path

import cv2
import pytesseract
from app.services.ocr_service import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)

CROPS_DIR = Path("data/layout_crops")
DETECTIONS_DIR = Path("data/layout_detections")
OUTPUT_DIR = Path("data/chart_extractions")


def extract_chart_text(image_path: Path) -> dict:
    """Extract visible labels and text from a YOLO-detected figure crop."""
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read chart image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    enlarged = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC,
    )

    text = pytesseract.image_to_string(
        enlarged,
        config="--oem 3 --psm 11",
    ).strip()

    ocr_data = pytesseract.image_to_data(
        enlarged,
        config="--oem 3 --psm 11",
        output_type=pytesseract.Output.DICT,
    )

    confidences = [
        float(value)
        for value, word in zip(ocr_data["conf"], ocr_data["text"])
        if word.strip() and value not in ("-1", "")
    ]

    return {
        "text": text,
        "mean_word_confidence": (
            round(sum(confidences) / len(confidences), 2)
            if confidences
            else None
        ),
        "ocr_engine": "tesseract",
        "preprocessing": "grayscale_2x",
    }


def extract_document_charts(document_id: str) -> dict:
    """Extract text from YOLO-detected Figure regions in a PDF."""
    detections_path = DETECTIONS_DIR / f"{document_id}.json"

    if not detections_path.is_file():
        raise FileNotFoundError(
            f"Layout detections not found: {detections_path}"
        )

    with detections_path.open("r", encoding="utf-8") as file:
        layout_data = json.load(file)

    document_crop_dir = CROPS_DIR / document_id
    chart_results = []

    for detection in layout_data.get("detections", []):
        if detection.get("label") != "Figure":
            continue

        page_number = detection["page_number"]
        crop_matches = sorted(
            document_crop_dir.glob(f"page_{page_number}_figure_*.png")
        )

        if not crop_matches:
            continue

        for crop_path in crop_matches:
            result = extract_chart_text(crop_path)

            chart_results.append({
                "page_number": page_number,
                "detection_confidence": detection["confidence"],
                "image_path": str(crop_path),
                **result,
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{document_id}.json"
    temporary_path = output_path.with_suffix(".tmp")

    output = {
        "document_id": document_id,
        "chart_count": len(chart_results),
        "charts": chart_results,
    }

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(output, file, ensure_ascii=False, indent=2)
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return {
        **output,
        "saved_to": str(output_path),
    }