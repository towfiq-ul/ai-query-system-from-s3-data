# ai-query-system-from-s3-data

Natural language search over Amazon S3 documents with AI-generated answers.

## Project Structure

```
ai-query-system-from-s3-data/
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

# 2. Start all services
make up

# 3. Wait for Ollama to pull llama3 (~5 mins on first start)
make logs-ollama

# 4. Create S3 bucket
make bucket

# 5. Upload documents
make upload FILE='docs/*'

# 6. Index uploaded documents
make index

# 7. Query
make query Q='What is the refund policy?'

# 8. Open chat UI
# http://localhost:3000
```

## Common Commands

```bash
make health                        # check all services
make ls-bucket                     # list uploaded files
make index-force                   # re-index all docs
make logs-api                      # tail API logs
make reload SVC=api                # hot reload a container
make down                          # stop all services
make clean                         # stop and delete all volumes
```

## Project Details
Please read the [article](ABOUT.md) on this project.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.