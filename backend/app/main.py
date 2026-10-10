import logging
import os
import sys
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s — %(message)s",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Garante que o Vercel consiga encontrar o módulo 'app' adicionando a raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.errors import unhandled_exception_handler
from pubmed.api.routes import router as pubmed_router
from pubmed.startup import warmup as pubmed_warmup
from app.api.routes import admin, analysis, auth, documents, feedback, health, methods, search
from app.config import get_settings
from app.db.connection import close_pool, create_pool


@asynccontextmanager
async def lifespan(_app: FastAPI):
    pool = None
    if get_settings().database_url:
        try:
            pool = await create_pool()
            _app.state.db_pool = pool
        except Exception as e:
            print(f"Database pool unavailable: {e}")

    import asyncio
    asyncio.create_task(pubmed_warmup())
    yield
    if pool is not None:
        await close_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    
    # Adiciona fallback para evitar que configurações ausentes quebrem o app
    is_production = settings.app_env == "production"
    app = FastAPI(
        title="Assist3R API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
    )

    cors_origins = settings.cors_origin_list

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(health.router)
    app.include_router(analysis.router)
    app.include_router(search.router)
    app.include_router(methods.router)
    app.include_router(documents.router)
    app.include_router(feedback.router)
    app.include_router(admin.router)
    app.include_router(auth.router)
    app.include_router(pubmed_router)

    return app


app = create_app()