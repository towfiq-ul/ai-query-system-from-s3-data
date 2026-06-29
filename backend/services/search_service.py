from opensearchpy import OpenSearch, RequestsHttpConnection
from sentence_transformers import SentenceTransformer
from services.parser_service import Chunk
from models.schemas import SourceReference, FileType
from core.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

INDEX_BODY = {
    "settings": {"index": {"knn": True, "knn.algo_param.ef_search": 100}},
    "mappings": {
        "properties": {
            "s3_key":      {"type": "keyword"},
            "file_type":   {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "text":        {"type": "text"},
            "embedding":   {"type": "knn_vector", "dimension": 384,
                            "method": {"name": "hnsw", "space_type": "cosinesimil",
                                       "engine": "nmslib"}},
        }
    },
}


class SearchService:
    def __init__(self):
        cfg = get_settings()
        self._index = cfg.opensearch_index
        self._model = SentenceTransformer(cfg.sentence_transformer_model, device="cpu")  # free, 384-dim
        self._client = OpenSearch(
            hosts=[{"host": cfg.opensearch_host, "port": cfg.opensearch_port}],
            http_auth=(cfg.opensearch_user, cfg.opensearch_password),
            use_ssl=False,
            connection_class=RequestsHttpConnection,
        )
        self._ensure_index()

    # ── Index management ──────────────────────────────────

    def _ensure_index(self):
        if not self._client.indices.exists(self._index):
            self._client.indices.create(index=self._index, body=INDEX_BODY)
            logger.info("Created OpenSearch index", extra={"index": self._index})

    def document_exists(self, s3_key: str) -> bool:
        result = self._client.count(
            index=self._index,
            body={"query": {"term": {"s3_key": s3_key}}}
        )
        return result["count"] > 0

    def document_chunk_count(self, s3_key: str) -> int:
        result = self._client.count(
            index=self._index,
            body={"query": {"term": {"s3_key": s3_key}}}
        )
        return result["count"]

    def index_chunks(self, chunks: list[Chunk]):
        texts = [c.text for c in chunks]
        embeddings = self._model.encode(texts, batch_size=32, show_progress_bar=False)
        bulk_body = []
        for chunk, embedding in zip(chunks, embeddings):
            bulk_body.append({"index": {"_index": self._index}})
            bulk_body.append({
                "s3_key":      chunk.s3_key,
                "file_type":   chunk.file_type,
                "chunk_index": chunk.chunk_index,
                "text":        chunk.text,
                "embedding":   embedding.tolist(),
            })
        self._client.bulk(body=bulk_body)
        logger.info("Indexed chunks", extra={"s3_key": chunks[0].s3_key, "count": len(chunks)})

    # ── Search ────────────────────────────────────────────

    def search(self, query: str, top_k: int) -> list[SourceReference]:
        query_vector = self._model.encode(query).tolist()
        response = self._client.search(
            index=self._index,
            body={
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {"vector": query_vector, "k": top_k}
                    }
                },
                "_source": ["s3_key", "file_type", "chunk_index", "text"],
            },
        )
        results = []
        for hit in response["hits"]["hits"]:
            src = hit["_source"]
            results.append(SourceReference(
                s3_key=src["s3_key"],
                file_type=FileType(src["file_type"]),
                chunk_index=src["chunk_index"],
                score=round(hit["_score"], 4),
                excerpt=src["text"][:300],
            ))
        return results

    @property
    def client(self):
        return self._client

    @property
    def index(self):
        return self._index
