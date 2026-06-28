from fastapi import APIRouter, HTTPException, Depends
from core.orchestrator import Orchestrator
from models.schemas import (
    QueryRequest, QueryResponse,
    IndexRequest, IndexResponse,
    HealthResponse,
)
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api")


def get_orchestrator() -> Orchestrator:
    # FastAPI dependency injection — one instance per request (stateless services)
    return Orchestrator()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, orch: Orchestrator = Depends(get_orchestrator)):
    """Accept a natural language question and return an AI-generated answer."""
    try:
        return orch.query(req)
    except Exception as exc:
        logger.error("Query failed", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail="Query pipeline failed. Check server logs.")


@router.post("/index", response_model=IndexResponse)
async def index(req: IndexRequest, orch: Orchestrator = Depends(get_orchestrator)):
    """Trigger indexing of all supported files in an S3 bucket/prefix."""
    try:
        return orch.index(req)
    except Exception as exc:
        logger.error("Index failed", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health", response_model=HealthResponse)
async def health():
    from services.cache_service import CacheService
    from services.search_service import SearchService
    from services.s3_service import S3Service

    cache = CacheService()

    opensearch_status = "ok"
    try:
        search = SearchService()
        count = search._client.count(index=search._index)
        opensearch_status = f"ok ({count['count']} docs)"
    except Exception as exc:
        opensearch_status = f"down: {str(exc)}"

    s3_status = "ok"
    try:
        s3 = S3Service()
        keys = list(s3.list_keys("docs/"))
        s3_status = f"ok ({len(keys)} files found)"
    except Exception as exc:
        s3_status = f"down: {str(exc)}"

    return HealthResponse(
        status="ok",
        services={
            "redis": cache.health(),
            "opensearch": opensearch_status,
            "s3": s3_status,
            "api": "ok",
        },
    )