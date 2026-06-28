# Makefile

.DEFAULT_GOAL := help

.PHONY: help up down logs build restart reload index index-force query opensearch health upload clean bucket ls-bucket upload install-backend frontend-dev ollama-pull

COMPOSE = docker-compose -f docker/docker-compose.yml
AWS_LOCAL = aws --endpoint-url=http://localhost:4566

# ── Lifecycle ─────────────────────────────────────────────────────────────────

up:
	$(COMPOSE) up

up-d:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) stop

down:
	$(COMPOSE) down

build:
	$(COMPOSE) up -d --build

restart:
	$(COMPOSE) restart

reload:
	@test -n "$(SVC)" || (echo "Usage: make reload SVC=api" && exit 1)
	$(COMPOSE) up -d --build --no-deps $(SVC)

clean:
	$(COMPOSE) down -v --remove-orphans

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
	$(COMPOSE) logs -f

logs-api:
	$(COMPOSE) logs -f api

logs-frontend:
	$(COMPOSE) logs -f frontend

logs-ollama:
	$(COMPOSE) logs -f ollama

logs-localstack:
	$(COMPOSE) logs -f localstack

# ── S3 (LocalStack) ───────────────────────────────────────────────────────────

bucket:
	$(AWS_LOCAL) s3 mb s3://local-bucket

ls-bucket:
	$(AWS_LOCAL) s3 ls s3://local-bucket --recursive

upload:
	@test -n "$(FILE)" || (echo "Usage: make upload FILE=docs/*" && exit 1)
	@for f in $(FILE); do \
		AWS_REQUEST_CHECKSUM_CALCULATION=when_required $(AWS_LOCAL) s3 cp $$f s3://local-bucket/docs/$$(basename $$f); \
	done

# ── API ───────────────────────────────────────────────────────────────────────

health:
	curl -s http://localhost:8000/api/health | python3 -m json.tool

index:
	curl -s -X POST http://localhost:8000/api/index \
		-H "Content-Type: application/json" \
		-d '{"bucket": "local-bucket", "prefix": "docs/", "force_reindex": false}' | python3 -m json.tool

index-force:
	curl -s -X POST http://localhost:8000/api/index \
		-H "Content-Type: application/json" \
		-d '{"bucket": "local-bucket", "prefix": "docs/", "force_reindex": true}' | python3 -m json.tool

query:
	@test -n "$(Q)" || (echo "Usage: make query Q='your question here'" && exit 1)
	curl -s -X POST http://localhost:8000/api/query \
		-H "Content-Type: application/json" \
		-d '{"question": "$(Q)", "top_k": 5}' | python3 -m json.tool

opensearch:
	curl -s http://localhost:9200/s3-rag-index/_count | python3 -m json.tool

# ── Dev ───────────────────────────────────────────────────────────────────────

install-backend:
	. backend/.venv/bin/activate
	pip install -r backend/requirements.txt

frontend-dev:
	cd frontend && npm install && npm run dev

ollama-pull:
	docker exec $$($(COMPOSE) ps -q ollama) ollama pull llama3

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  RAG — Available Commands"
	@echo ""
	@echo "  Lifecycle"
	@echo "    make up                        Start all services (detached)"
	@echo "    make down                      Stop all services"
	@echo "    make build                     Rebuild images and start"
	@echo "    make restart                   Restart all services"
	@echo "    make clean                     Stop and delete all volumes"
	@echo ""
	@echo "  Logs"
	@echo "    make logs                      Tail all service logs"
	@echo "    make logs-api                  Tail API logs only"
	@echo "    make logs-ollama               Monitor llama3 pull progress"
	@echo "    make logs-localstack           Tail LocalStack logs"
	@echo ""
	@echo "  S3 (LocalStack)"
	@echo "    make bucket                    Create local-bucket in LocalStack"
	@echo "    make ls-bucket                 List all files in the bucket"
	@echo "    make upload FILE='docs/*'      Upload one or multiple files to S3. FILE='docs/*', FILE='docs/*.pdf' etc"
	@echo ""
	@echo "  API"
	@echo "    make health                    Check service health"
	@echo "    make index                     Index all docs under docs/ prefix"
	@echo "    make index-force               Index all docs under docs/ prefix forcefully"
	@echo "    make query Q='your question'   Run a natural language query"
	@echo "    make opensearch   			  Check service opensearch"
	@echo ""
	@echo "  Dev"
	@echo "    make install-backend           pip install backend dependencies"
	@echo "    make frontend-dev              Run frontend locally outside Docker"
	@echo "    make ollama-pull               Manually pull llama3 into running container"
	@echo "    make reload SVC=api            Rebuild and restart a single container. SVC=api/frontend"
	@echo ""