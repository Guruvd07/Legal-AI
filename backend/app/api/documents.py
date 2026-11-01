
import json
import uuid
from pathlib import Path

import fitz
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/uploads")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    original_filename = Path(file.filename).name

    if Path(original_filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    document_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{document_id}.pdf"
    metadata_path = UPLOAD_DIR / f"{document_id}.json"

    size = 0

    try:
        # Save the PDF using its unique document ID.
        with file_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 20 MB limit",
                    )

                output.write(chunk)

        # Validate the uploaded PDF.
        with fitz.open(file_path) as pdf:
            page_count = len(pdf)

            if page_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="PDF contains no pages",
                )

        # Save the original filename for later indexing.
        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            json.dump(
                {
                    "document_id": document_id,
                    "filename": original_filename,
                },
                metadata_file,
                ensure_ascii=False,
                indent=2,
            )

    except HTTPException:
        file_path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)
        raise

    except Exception:
        file_path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Invalid, corrupted, or unsupported PDF",
        )

    finally:
        await file.close()

    return {
        "document_id": document_id,
        "filename": original_filename,
        "page_count": page_count,
        "size_bytes": size,
        "status": "uploaded",
        "message": "PDF uploaded and validated successfully",
    }
