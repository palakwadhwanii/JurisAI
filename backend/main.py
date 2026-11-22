import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import time
from fastapi.responses import Response
from backend.routes.analysis import router as analysis_router
from backend.routes.auth import router as auth_router
from observability.logging_config import setup_logging, get_logger, current_analysis_id
from observability.metrics import (
    API_REQUESTS_TOTAL,
    API_REQUEST_DURATION_SECONDS,
    get_prometheus_metrics,
    CONTENT_TYPE_LATEST
)

from contextlib import asynccontextmanager
import threading
from backend.services.jurisai_engine import get_engine

# Initialize structured logging to logs/jurisai_app.log
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
app_logger = setup_logging(log_file=LOGS_DIR / "jurisai_app.log")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm singleton engine on background thread at startup
    threading.Thread(target=get_engine, daemon=True).start()
    yield

app = FastAPI(
    title="JurisAI: Indian Family Law Multi-Agent System",
    description="Constraint-Aware Legal Reasoning & Self-Checking Multi-Agent Analysis across 12 Central Indian Acts.",
    version="1.0.0",
    lifespan=lifespan
)

# HTTP Request Metrics Middleware
@app.middleware("http")
async def prometheus_metrics_middleware(request, call_next):
    start_time = time.perf_counter()
    method = request.method
    endpoint = request.url.path

    # Extract or set analysis_id if header passed
    req_analysis_id = request.headers.get("X-Analysis-ID")
    if req_analysis_id:
        current_analysis_id.set(req_analysis_id)

    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        app_logger.error(f"Unhandled HTTP error on {method} {endpoint}: {str(e)}", extra={"status": "ERROR"})
        raise
    finally:
        dur = time.perf_counter() - start_time
        API_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        API_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(dur)

# Expose /metrics for Prometheus scraping
@app.get("/metrics", tags=["Observability"])
def metrics_endpoint():
    """Prometheus metrics scrape endpoint."""
    return Response(content=get_prometheus_metrics(), media_type=CONTENT_TYPE_LATEST)

# Enable CORS with dynamic origin support (allows Vercel frontend, local dev, or custom domains)
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env and cors_origins_env.strip() != "*":
    cors_origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Match all HTTP/HTTPS origins so Vercel deployments & preview URLs work seamlessly
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include analysis and auth API routes
app.include_router(analysis_router)
app.include_router(auth_router)

# Mount frontend build if available
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.api_route("/", methods=["GET", "HEAD"])
    def root():
        return {
            "project": "JurisAI: Multi-Agent Constraint-Aware Legal Reasoning",
            "team": "Student Engineering Project",
            "statutes": "12 Central Indian Family Law Acts",
            "precedents": "91 Supreme Court Judgments (2023-2025)",
            "api_docs": "/docs",
            "health_check": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
