from pydantic import BaseModel, Field
from typing import Optional


# ── Request Schemas ──────────────────────────────────────────

class QueryRequest(BaseModel):
    """Payload for the /query endpoint."""
    question: str = Field(..., min_length=1, description="The user's question about the uploaded document.")
    document_id: str = Field(..., min_length=1, description="ID returned from the /upload endpoint.")


# ── Response Schemas ─────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"


class UploadResponse(BaseModel):
    """Returned after a successful document upload + indexing."""
    document_id: str
    filename: str
    page_count: int
    message: str = "Document indexed successfully."


class QueryResponse(BaseModel):
    """Returned from the /query endpoint."""
    document_id: str
    question: str
    answer: str
    model: str = "mercury-2"


class ErrorResponse(BaseModel):
    detail: str
