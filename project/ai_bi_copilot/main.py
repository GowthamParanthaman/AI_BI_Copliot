from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from loguru import logger

from core.config import settings
from database.init_db import init_db

from api.routes.analysis import (
    router as analysis_router,
)
from api.routes.datasets import (
    router as dataset_router,
)
from api.routes.health import (
    router as health_router,
)
from api.routes.upload import (
    router as upload_router,
)

# -- Paths --
_BASE = Path(__file__).resolve().parent
# dashboard.html has no template variables — serve as plain HTML to avoid
# Jinja2 3.1.6 LRU cache-key bug with dict globals in Starlette < 0.46
_DASHBOARD_HTML = (_BASE / "templates" / "dashboard.html").read_text(encoding="utf-8")

# =====================================================
# APPLICATION LIFECYCLE
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=" * 80)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info("=" * 80)

    try:
        init_db()
        logger.success("Database initialized successfully")

        logger.info("Registered API Routes")
        for route in app.routes:
            logger.info(f"{getattr(route, 'path', '')}")

        logger.success("Application initialized successfully")

    except Exception as exc:
        logger.exception(f"Application startup failed: {exc}")
        raise

    yield

    logger.info("=" * 80)
    logger.info(f"Stopping {settings.APP_NAME}")
    logger.info("=" * 80)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description="""
# AI Business Intelligence Copilot

Enterprise AI-powered analytics platform.

## Features

- Dataset Upload
- Dataset Management
- Data Validation
- Data Profiling
- Business KPI Detection
- Trend Analysis
- Insight Generation
- Recommendation Engine
- Executive Reporting
- Dashboard Generation
- LangGraph Agent Workflow
- AI Business Copilot
""",
)

# =====================================================
# STATIC FILES
# =====================================================

_STATIC = _BASE / "static"
_STATIC.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

_CHARTS = _BASE / "reports" / "charts"
_CHARTS.mkdir(parents=True, exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(_CHARTS)), name="charts")

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GLOBAL EXCEPTION HANDLER
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal Server Error",
            "error": str(exc),
        },
    )

# =====================================================
# ROUTE REGISTRATION
# =====================================================

app.include_router(health_router)
app.include_router(dataset_router)
app.include_router(upload_router)
app.include_router(analysis_router)

# =====================================================
# DASHBOARD (root)
# =====================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return HTMLResponse(content=_DASHBOARD_HTML)

# =====================================================
# SYSTEM PROBES
# =====================================================

@app.get("/ready", tags=["System"], summary="Readiness Probe")
async def readiness():
    return {"status": "ready"}

@app.get("/live", tags=["System"], summary="Liveness Probe")
async def liveness():
    return {"status": "alive"}

@app.get("/version", tags=["System"])
async def version():
    return {"application": settings.APP_NAME, "version": "1.0.0"}
