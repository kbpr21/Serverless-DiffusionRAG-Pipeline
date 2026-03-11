"""
main.py — Serverless DiffusionRAG Pipeline
FastAPI entry-point that exposes /health, /upload, and /query endpoints.
"""

import logging
import json
import os
import time

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# ── Structured JSON Logging ──────────────────────────────────

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "method"):
            log_entry["method"] = record.method
            log_entry["path"] = record.path
            log_entry["status_code"] = record.status_code
            log_entry["duration_ms"] = record.duration_ms
        return json.dumps(log_entry)

logger = logging.getLogger("diffusionrag")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

from app.schemas import (
    HealthResponse,
    UploadResponse,
    QueryRequest,
    QueryResponse,
    ErrorResponse,
)
from app.services.retrieval import ingest_document, get_document_context
from app.services.llm import generate_answer


app = FastAPI(
    title="Serverless DiffusionRAG Pipeline",
    description=(
        "A cost-optimized RAG API using VectifyAI PageIndex "
        "for vectorless retrieval and Mercury 2 dLLM for inference."
    ),
    version="0.1.0",
)

# ── CORS Middleware ──────────────────────────────────────────

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ── Request Logging Middleware ──────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


# ── Health Check ─────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Returns a simple health status to verify the service is running."""
    return HealthResponse()


# ── Document Upload ──────────────────────────────────────────

@app.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Documents"],
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document.
    The file is parsed in-memory and indexed using PageIndex.
    Returns a document_id to use with /query.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    allowed = {"pdf", "txt"}
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}. Allowed: {', '.join(allowed)}",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        metadata = await ingest_document(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UploadResponse(**metadata)


# ── Query ────────────────────────────────────────────────────

@app.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
    tags=["RAG"],
)
async def query_document(body: QueryRequest):
    """
    Ask a question about a previously uploaded document.
    Uses PageIndex to retrieve relevant context, then routes
    it to Mercury 2 for reasoning and answer generation.
    """
    try:
        context = get_document_context(body.document_id, body.question)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        result = await generate_answer(context, body.question)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Mercury 2 API error: {str(e)}",
        )

    return QueryResponse(
        document_id=body.document_id,
        question=body.question,
        answer=result["answer"],
        model=result["model"],
    )
