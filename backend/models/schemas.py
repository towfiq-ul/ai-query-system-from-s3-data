from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    CSV = "csv"
    JSON = "json"
    MD = "md"


# ── Requests ──────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Natural language question")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    include_sources: bool = Field(default=True, description="Return source references")


class IndexRequest(BaseModel):
    bucket: str = Field(..., description="S3 bucket name")
    prefix: str = Field(default="", description="S3 key prefix to scope indexing")
    force_reindex: bool = Field(default=False, description="Re-index even if already indexed")


# ── Inner models ──────────────────────────────────────────

class SourceReference(BaseModel):
    s3_key: str
    file_type: FileType
    chunk_index: int
    score: float
    excerpt: str = Field(..., description="Relevant text snippet from the chunk")


class IndexedFile(BaseModel):
    s3_key: str
    file_type: FileType
    chunk_count: int
    status: str  # "indexed" | "skipped" | "failed"


# ── Responses ─────────────────────────────────────────────

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = []
    cached: bool = False
    latency_ms: int


class IndexResponse(BaseModel):
    files: list[IndexedFile]
    total_chunks: int
    message: str


class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]  # service_name -> "ok" | "degraded" | "down"
