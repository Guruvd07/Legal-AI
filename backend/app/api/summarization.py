
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.summarizer_service import summarize_document


router = APIRouter(
    prefix="/api/documents",
    tags=["Document Summarization"],
)


@router.post("/{document_id}/summarize")
def summarize_uploaded_document(document_id: str):
    try:
        UUID(document_id)

        return summarize_document(document_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Uploaded PDF not found. Upload the document first.",
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document summarization failed. Check backend terminal logs.",
        )
