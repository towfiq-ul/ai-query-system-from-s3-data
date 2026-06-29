import io
import csv
import json
from dataclasses import dataclass
from core.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    text: str
    chunk_index: int
    s3_key: str
    file_type: str

# ── Extractors ────────────────────────────────────────
def _extract_pdf(raw_bytes: bytes) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_txt(raw_bytes: bytes) -> str:
    return raw_bytes.decode("utf-8", errors="replace")


def _extract_csv(raw_bytes: bytes) -> str:
    reader = csv.DictReader(io.StringIO(raw_bytes.decode("utf-8", errors="replace")))
    rows = []
    for row in reader:
        rows.append(", ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(rows)


def _extract_json(raw_bytes: bytes) -> str:
    data = json.loads(raw_bytes.decode("utf-8", errors="replace"))
    return json.dumps(data, indent=2)


class ParserService:
    def __init__(self):
        cfg = get_settings()
        self._chunk_size = cfg.max_chunk_size
        self._overlap = cfg.chunk_overlap

    # ── Public ────────────────────────────────────────────

    def parse_and_chunk(self, key: str, raw_bytes: bytes) -> list[Chunk]:
        ext = key.rsplit(".", 1)[-1].lower() if "." in key else ""
        extractors = {
            "pdf": _extract_pdf,
            "txt": _extract_txt,
            "csv": _extract_csv,
            "json": _extract_json,
            "md": _extract_txt,
        }
        extractor = extractors.get(ext)
        if not extractor:
            logger.warning("Unsupported file type", extra={"key": key, "ext": ext})
            return []

        full_text = extractor(raw_bytes)
        return self._chunk_text(full_text, key, ext)

    # ── Chunker ───────────────────────────────────────────

    def _chunk_text(self, text: str, key: str, file_type: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(text=chunk_text, chunk_index=idx, s3_key=key, file_type=file_type))
                idx += 1
            start = end - self._overlap if end < len(text) else end
        return chunks
