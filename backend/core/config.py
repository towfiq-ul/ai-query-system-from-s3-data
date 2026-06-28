from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # AWS
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "local-bucket"
    aws_endpoint_url: str = "http://localstack:4566"

    # OpenSearch
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_index: str = "s3-rag-index"
    opensearch_user: str = "admin"
    opensearch_password: str = "admin"

    # LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl_seconds: int = 3600

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
