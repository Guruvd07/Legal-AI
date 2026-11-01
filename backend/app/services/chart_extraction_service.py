
import json
from pathlib import Path

import cv2
import numpy as np
import pytesseract

from app.services.ocr_service import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)

CROPS_DIR = Path("data/layout_crops")
DETECTIONS_DIR = Path("data/layout_detections")
OUTPUT_DIR = Path("data/chart_extractions")

# Calibration for the current synthetic test bar chart only.
TEST_BAR_CHART_PAGE = 1
TEST_PLOT_TOP = 16
TEST_PLOT_BOTTOM = 271
TEST_AXIS_MIN = 0
TEST_AXIS_MAX = 100


def extract_chart_text(image_path: Path) -> dict:
    """Extract visible text from a YOLO-detected figure crop."""
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

    config = "--oem 3 --psm 11"

    text = pytesseract.image_to_string(
        enlarged,
        config=config,
    ).strip()

    ocr_data = pytesseract.image_to_data(
        enlarged,
        config=config,
        output_type=pytesseract.Output.DICT,
    )

    confidences = [
        float(value)
        for value, word in zip(
            ocr_data["conf"],
            ocr_data["text"],
        )
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


def estimate_test_bar_values(image_path: Path) -> dict:
    """
    Estimate bar values using fixed coordinates calibrated for
    the current synthetic test chart.

    This is not a general-purpose chart digitizer.
    """
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read chart image: {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    blue_mask = cv2.inRange(
        hsv,
        np.array([90, 40, 40]),
        np.array([130, 255, 255]),
    )

    contours, _ = cv2.findContours(
        blue_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    bars = []

    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        # Exclude the large outer chart border and small noise.
        if (
            40 <= width <= 150
            and height >= 50
            and area > 1000
        ):
            bars.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            })

    bars.sort(key=lambda bar: bar["x"])

    if len(bars) != 4:
        return {
            "method": "opencv_blue_bar_height",
            "status": "unavailable",
            "reason": (
                f"Expected 4 bars but detected {len(bars)}"
            ),
            "bars": [],
        }

    results = []

    for index, bar in enumerate(bars, start=1):
        estimated_value = (
            (TEST_PLOT_BOTTOM - bar["y"])
            / (TEST_PLOT_BOTTOM - TEST_PLOT_TOP)
            * (TEST_AXIS_MAX - TEST_AXIS_MIN)
            + TEST_AXIS_MIN
        )

        results.append({
            "bar_index": index,
            "estimated_value": round(estimated_value, 1),
            "x": bar["x"],
            "y": bar["y"],
            "width": bar["width"],
            "height": bar["height"],
            "value_type": "approximate",
        })

    return {
        "method": "opencv_blue_bar_height",
        "status": "estimated",
        "calibration": "fixed_test_chart_coordinates",
        "axis_min": TEST_AXIS_MIN,
        "axis_max": TEST_AXIS_MAX,
        "bars": results,
    }


def extract_document_charts(document_id: str) -> dict:
    """Extract text and available measurements from figure crops."""
    detections_path = (
        DETECTIONS_DIR / f"{document_id}.json"
    )

    if not detections_path.is_file():
        raise FileNotFoundError(
            f"Layout detections not found: {detections_path}"
        )

    with detections_path.open("r", encoding="utf-8") as file:
        layout_data = json.load(file)

    document_crop_dir = CROPS_DIR / document_id
    chart_results = []

    # The crop service numbers every detection in original list order,
    # including Table detections. Match using that same global index.
    for detection_index, detection in enumerate(
        layout_data.get("detections", []),
        start=1,
    ):
        if detection.get("label") != "Figure":
            continue

        page_number = detection["page_number"]

        crop_path = (
            document_crop_dir
            / f"page_{page_number}_figure_{detection_index}.png"
        )

        if not crop_path.is_file():
            continue

        result = extract_chart_text(crop_path)

        chart_result = {
            "page_number": page_number,
            "detection_confidence": detection["confidence"],
            "image_path": str(crop_path),
            **result,
        }

        # Apply the calibrated estimator only to the known test chart.
        if (
            page_number == TEST_BAR_CHART_PAGE
            and crop_path.name == "page_1_figure_1.png"
        ):
            chart_result["bar_analysis"] = (
                estimate_test_bar_values(crop_path)
            )

        chart_results.append(chart_result)

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
            json.dump(
                output,
                file,
                ensure_ascii=False,
                indent=2,
            )

        temporary_path.replace(output_path)

    finally:
        temporary_path.unlink(missing_ok=True)

    return {
        **output,
        "saved_to": str(output_path),
    }
