import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import load_settings


settings = load_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Memento Notes API started")
    yield


app = FastAPI(
    title=settings.app_name,
    description="A minimal local notes service powered by FastAPI.",
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/version")
async def version() -> dict[str, str]:
    logger.info("Version requested")
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
    }
