from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="RAG API",
    description="Natural language search over Amazon S3 documents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production via env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    logger.info("RAG API started")
