# Setup Guide

## Prerequisites
- Docker + Docker Compose
- AWS account with S3 bucket and IAM credentials
- 8 GB RAM minimum (for Ollama + OpenSearch)

## 1. Configure environment

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-docs-bucket
```

## 2. Start services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

Services started:
| Service    | Port  | Purpose                    |
|------------|-------|----------------------------|
| API        | 8000  | FastAPI backend             |
| OpenSearch | 9200  | Vector index               |
| Redis      | 6379  | Query cache                |
| Ollama     | 11434 | Local LLM (llama3)         |
| Frontend   | 3000  | React chat UI              |

Ollama pulls `llama3` (~4.7 GB) on first start. Wait ~5 minutes.

## 3. Index your S3 documents

```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"bucket": "my-docs-bucket", "prefix": "docs/"}'
```

Response:
```json
{
  "files": [{"s3_key": "docs/manual.pdf", "file_type": "pdf", "chunk_count": 42, "status": "indexed"}],
  "total_chunks": 42,
  "message": "Indexed 42 chunks from 1 files."
}
```

## 4. Query

Open http://localhost:3000 or:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the return policy?", "top_k": 5}'
```

## 5. Health check

```bash
curl http://localhost:8000/api/health
```

## IAM Policy (minimum required)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::my-docs-bucket",
      "arn:aws:s3:::my-docs-bucket/*"
    ]
  }]
}
```

## Production notes

- Set `plugins.security.disabled=false` in OpenSearch and add TLS certs
- Replace `allow_origins=["*"]` in `main.py` with your frontend domain
- Use AWS Secrets Manager instead of `.env` for credentials
- Add a load balancer in front of the API for horizontal scaling
- Switch `OLLAMA_MODEL=llama3` to a larger model for higher answer quality
