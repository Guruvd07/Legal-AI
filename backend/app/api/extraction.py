
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.services.pdf_extractor import extract_pdf_text

router = APIRouter(prefix="/api/documents", tags=["PDF Extraction"])

UPLOAD_DIR = Path("data/uploads")


@router.get("/{document_id}/text")
def get_document_text(document_id: str):
    # Accept only UUID-shaped document IDs.
    import uuid

    try:
        parsed_id = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    file_path = UPLOAD_DIR / f"{parsed_id}.pdf"

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        return extract_pdf_text(str(file_path))
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from this PDF",
        )
