import time
from services.s3_service import S3Service
from services.parser_service import ParserService
from services.search_service import SearchService
from services.llm_service import LLMService
from services.cache_service import CacheService
from models.schemas import (
    QueryRequest, QueryResponse,
    IndexRequest, IndexResponse,
    IndexedFile, FileType,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self):
        self._s3 = S3Service()
        self._parser = ParserService()
        self._search = SearchService()
        self._llm = LLMService()
        self._cache = CacheService()

    # ── Query pipeline ────────────────────────────────────

    def query(self, req: QueryRequest) -> QueryResponse:
        start = time.monotonic()

        # 1. Cache hit
        cached = self._cache.get(req.question, req.top_k)
        if cached:
            logger.info("Cache hit", extra={"question": req.question})
            return QueryResponse(**{**cached, "cached": True,
                                    "latency_ms": int((time.monotonic() - start) * 1000)})

        # 2. Extract keywords (helps with hybrid search intent)
        keywords = self._llm.extract_keywords(req.question)
        logger.info("Extracted keywords", extra={"keywords": keywords})

        # 3. Vector search over indexed chunks
        sources = self._search.search(req.question, req.top_k)
        if not sources:
            return QueryResponse(
                answer="No relevant documents found for your question.",
                sources=[],
                cached=False,
                latency_ms=int((time.monotonic() - start) * 1000),
            )

        # 4. Generate grounded answer
        context_chunks = [f"[Source: {s.s3_key}]\n{s.excerpt}" for s in sources]
        answer = self._llm.generate_answer(req.question, context_chunks)

        # 5. Build response
        response_dict = {
            "answer": answer,
            "sources": [s.model_dump() for s in sources] if req.include_sources else [],
        }
        self._cache.set(req.question, req.top_k, response_dict)

        return QueryResponse(
            **response_dict,
            cached=False,
            latency_ms=int((time.monotonic() - start) * 1000),
        )

    # ── Index pipeline ────────────────────────────────────

    def index(self, req: IndexRequest) -> IndexResponse:
        indexed_files: list[IndexedFile] = []
        total_chunks = 0

        for key in self._s3.list_keys(req.prefix):
            ext = key.rsplit(".", 1)[-1].lower() if "." in key else ""

            if not req.force_reindex and self._search.document_exists(key) and self._search.document_chunk_count(key) > 0:
                indexed_files.append(IndexedFile(
                    s3_key=key, file_type=FileType(ext), chunk_count=0, status="skipped"
                ))
                continue

            try:
                raw_bytes = self._s3.download_bytes(key)
                chunks = self._parser.parse_and_chunk(key, raw_bytes)
                if chunks:
                    self._search.index_chunks(chunks)
                    total_chunks += len(chunks)
                indexed_files.append(IndexedFile(
                    s3_key=key, file_type=FileType(ext), chunk_count=len(chunks), status="indexed"
                ))
            except Exception as exc:
                logger.error("Failed to index file", extra={"key": key, "error": str(exc)})
                indexed_files.append(IndexedFile(
                    s3_key=key, file_type=FileType(ext), chunk_count=0, status="failed"
                ))

        return IndexResponse(
            files=indexed_files,
            total_chunks=total_chunks,
            message=f"Indexed {total_chunks} chunks from {len(indexed_files)} files.",
        )
