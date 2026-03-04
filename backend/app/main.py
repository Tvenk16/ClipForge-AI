"""
ClipForge AI FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks. TODO: Production - health check Redis on startup."""
    yield


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    app = FastAPI(
        title="ClipForge AI",
        description="Agentic YouTube Shorts automation API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix=settings.API_PREFIX)
    return app


app = create_app()


@app.get("/")
def root() -> dict:
    """Health/root endpoint."""
    return {"service": "ClipForge AI", "status": "ok"}
