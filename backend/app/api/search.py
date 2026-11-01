
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.vector_store import search_chunks

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)
    document_id: str | None = Field(default=None, min_length=1)


@router.post("/query")
def search_documents(request: SearchRequest):
    try:
        results = search_chunks(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )

        return {
            "query": request.query,
            "document_id": request.document_id,
            "result_count": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Semantic search failed",
        )
