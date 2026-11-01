
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag_service import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/questions",
    tags=["RAG Question Answering"],
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)
    document_id: str | None = Field(default=None, min_length=1)

@router.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        return answer_question(
            
            question=request.question,
            top_k=request.top_k,
            document_id=request.document_id,
        )

    except RuntimeError as exc:
        logger.exception("RAG runtime/configuration error")
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except Exception:
        logger.exception("RAG question-answering failed")
        raise HTTPException(
            status_code=500,
            detail="Question answering failed. Check backend terminal logs.",
        )
