import httpx
from core.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful document assistant. "
    "Answer the user's question using the provided context. "
    "If the context contains partial information, use it and clearly state what is and isn't covered. "
    "List filenames, keys, or document names when asked about available files. "
    "Do not hallucinate facts not present in the context."
)


class LLMService:
    def __init__(self):
        cfg = get_settings()
        self._provider = cfg.llm_provider
        self._ollama_url = cfg.ollama_base_url
        self._ollama_model = cfg.ollama_model

    def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        context = "\n\n---\n\n".join(context_chunks)
        user_message = f"Context:\n{context}\n\nQuestion: {question}"
        if self._provider == "ollama":
            return self._call_ollama(user_message)
        raise ValueError(f"Unsupported LLM provider: {self._provider}")

    def extract_keywords(self, question: str) -> list[str]:
        """Ask the LLM to extract search keywords from a natural language question."""
        prompt = (
            f"Extract 3-6 concise search keywords from this question. "
            f"Return them as a comma-separated list and nothing else.\n\nQuestion: {question}"
        )
        raw = self._call_ollama(prompt)
        return [kw.strip() for kw in raw.split(",") if kw.strip()]

    # ── Providers ─────────────────────────────────────────

    def _call_ollama(self, user_message: str) -> str:
        payload = {
            "model": self._ollama_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }
        try:
            with httpx.Client(timeout=120) as client:
                response = client.post(f"{self._ollama_url}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"].strip()
        except httpx.HTTPError as exc:
            logger.error("Ollama request failed", extra={"error": str(exc)})
            raise RuntimeError(f"LLM call failed: {exc}") from exc
