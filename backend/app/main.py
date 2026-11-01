
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.documents import router as documents_router
from app.api.extraction import router as extraction_router
from app.api.indexing import router as indexing_router
from app.api.search import router as search_router
from app.api.questions import router as questions_router
from app.api.summarization import router as summarization_router

app = FastAPI(
    title="LegalAI API",
    description="AI-powered legal document summarization and intelligence",
    version="1.0.0",
)

app.include_router(documents_router)
app.include_router(extraction_router)
app.include_router(indexing_router)
app.include_router(search_router)
app.include_router(questions_router)
app.include_router(summarization_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "LegalAI API is running",
        "status": "success",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LegalAI Backend",
    }
