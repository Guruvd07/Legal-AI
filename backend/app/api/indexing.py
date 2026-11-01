import json
from pathlib import Path
import uuid

from fastapi import APIRouter, HTTPException
from app.services.layout_crop_service import crop_document_layout
from app.services.layout_detection_service import detect_document_layout
from app.services.document_indexer import index_document
from app.services.table_ocr_service import extract_document_tables
from app.services.chart_extraction_service import extract_document_charts


router = APIRouter(
    prefix="/api/documents",
    tags=["Document Indexing"]
)


# ============================================================
# 1. DOCUMENT INDEXING
# ============================================================

@router.post("/{document_id}/index")
def index_uploaded_document(document_id: str):

    try:
        document_id = str(uuid.UUID(document_id))

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    try:
        return index_document(document_id)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document indexing failed"
        )


# ============================================================
# 2. YOLO LAYOUT DETECTION
# ============================================================

@router.post("/{document_id}/layout-detection")
def detect_uploaded_document_layout(document_id: str):

    try:
        document_id = str(uuid.UUID(document_id))

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    pdf_path = Path("data/uploads") / f"{document_id}.pdf"

    if not pdf_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    try:
        result = detect_document_layout(str(pdf_path))

        output_dir = Path("data/layout_detections")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{document_id}.json"
        temporary_path = output_path.with_suffix(".tmp")

        try:
            with temporary_path.open(
                "w",
                encoding="utf-8"
            ) as output_file:

                json.dump(
                    result,
                    output_file,
                    ensure_ascii=False,
                    indent=2
                )

            temporary_path.replace(output_path)

        finally:
            temporary_path.unlink(missing_ok=True)

        # Generate cropped images for detected tables and figures
        crop_result = crop_document_layout(document_id)

        return {
            **result,
            "status": "completed",
            "saved_to": str(output_path),
            "crop_count": crop_result["crop_count"],
            "crops": crop_result["crops"]
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="PDF or YOLO model not found"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document layout detection failed"
        )


# ============================================================
# 3. TABLE OCR EXTRACTION
# ============================================================

@router.post("/{document_id}/table-extraction")
def extract_uploaded_document_tables(document_id: str):

    try:
        document_id = str(uuid.UUID(document_id))

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    try:
        result = extract_document_tables(document_id)

        return {
            **result,
            "status": "completed"
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Layout detections or table crops not found"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Table extraction failed"
        )


# ============================================================
# 4. CHART EXTRACTION
# ============================================================

@router.post("/{document_id}/chart-extraction")
def extract_uploaded_document_charts(document_id: str):

    try:
        document_id = str(uuid.UUID(document_id))

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    try:
        result = extract_document_charts(document_id)

        return {
            **result,
            "status": "completed"
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Layout detections or chart crops not found"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Chart extraction failed"
        )