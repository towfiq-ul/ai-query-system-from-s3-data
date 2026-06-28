# ai-query-system-from-s3-data

Natural language search over Amazon S3 documents with AI-generated answers.

## Project Structure

```
s3-rag/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # FastAPI route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # App configuration & env vars
│   │   └── orchestrator.py        # AI pipeline coordinator
│   ├── services/
│   │   ├── __init__.py
│   │   ├── s3_service.py          # S3 file fetching & listing
│   │   ├── parser_service.py      # PDF/TXT/CSV/JSON extraction
│   │   ├── search_service.py      # OpenSearch vector search
│   │   ├── llm_service.py         # LLM calls (Ollama/HuggingFace)
│   │   └── cache_service.py       # Redis caching layer
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic request/response models
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py              # Structured logging
│   ├── main.py                    # FastAPI app entrypoint
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatInterface.jsx   # Main chat UI
│       │   ├── MessageBubble.jsx   # User/AI message display
│       │   └── SourceCard.jsx      # Source reference display
│       ├── hooks/
│       │   └── useChat.js          # Chat state & API calls
│       ├── utils/
│       │   └── api.js              # Axios API client
│       └── App.jsx
├── docker/
│   ├── docker-compose.yml          # All services orchestration
│   └── opensearch.yml              # OpenSearch config
└── docs/
    └── SETUP.md                    # Deployment guide
```

## Quick Start

```bash
# 1. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your AWS credentials

# 2. Start all services
docker-compose -f docker/docker-compose.yml up -d

# 3. Index your S3 documents
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"bucket": "your-bucket", "prefix": "docs/"}'

# 4. Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?"}'
```
