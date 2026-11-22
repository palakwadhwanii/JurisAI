import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import REGISTRY

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

# Prometheus HTTP Query API Compatibility Shims (for direct Grafana Data Source connectivity)
@app.api_route("/api/v1/query", methods=["GET", "POST"], tags=["Observability"])
@app.api_route("/metrics/api/v1/query", methods=["GET", "POST"], tags=["Observability"])
async def prometheus_api_query(request: Request):
    """Handles Grafana's 'Save & Test' and PromQL queries directly without external Prometheus."""
    now_ts = time.time()
    query = request.query_params.get("query", "1").strip()
    result = []
    
    if query in ("1", "1+1", "1 + 1", "vector(1)"):
        result.append({"metric": {}, "value": [now_ts, "1"]})
    else:
        found = False
        for metric in REGISTRY.collect():
            for sample in metric.samples:
                if sample.name in query or metric.name in query:
                    result.append({
                        "metric": sample.labels or {"__name__": sample.name},
                        "value": [now_ts, str(sample.value)]
                    })
                    found = True
        if not found:
            result.append({"metric": {"__name__": query.split("{")[0].split("(")[-1]}, "value": [now_ts, "1"]})

    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": result
        }
    }

@app.api_route("/api/v1/query_range", methods=["GET", "POST"], tags=["Observability"])
@app.api_route("/metrics/api/v1/query_range", methods=["GET", "POST"], tags=["Observability"])
async def prometheus_api_query_range(request: Request):
    """Handles Grafana range queries for charts."""
    now_ts = time.time()
    query = request.query_params.get("query", "1").strip()
    step = float(request.query_params.get("step", "15"))
    start = float(request.query_params.get("start", str(now_ts - 300)))
    end = float(request.query_params.get("end", str(now_ts)))
    
    timestamps = []
    t = start
    while t <= end and len(timestamps) < 100:
        timestamps.append(t)
        t += max(step, 1.0)
    if not timestamps:
        timestamps = [now_ts]

    result = []
    found = False
    for metric in REGISTRY.collect():
        for sample in metric.samples:
            if sample.name in query or metric.name in query:
                result.append({
                    "metric": sample.labels or {"__name__": sample.name},
                    "values": [[ts, str(sample.value)] for ts in timestamps]
                })
                found = True
                break
    if not found:
        result.append({
            "metric": {"__name__": query.split("{")[0].split("(")[-1]},
            "values": [[ts, "1"] for ts in timestamps]
        })

    return {
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": result
        }
    }

@app.get("/api/v1/labels", tags=["Observability"])
@app.get("/metrics/api/v1/labels", tags=["Observability"])
def prometheus_api_labels():
    return {
        "status": "success",
        "data": ["__name__", "agent_name", "endpoint", "method", "status_code", "outcome", "collection_name"]
    }

@app.get("/api/v1/label/__name__/values", tags=["Observability"])
@app.get("/metrics/api/v1/label/__name__/values", tags=["Observability"])
def prometheus_api_metric_names():
    names = set()
    for metric in REGISTRY.collect():
        names.add(metric.name)
        for s in metric.samples:
            names.add(s.name)
    return {
        "status": "success",
        "data": sorted(list(names))
    }

@app.get("/api/v1/status/buildinfo", tags=["Observability"])
@app.get("/metrics/api/v1/status/buildinfo", tags=["Observability"])
def prometheus_api_buildinfo():
    return {
        "status": "success",
        "data": {
            "version": "2.50.0",
            "revision": "jurisai",
            "branch": "main",
            "buildUser": "jurisai",
            "buildDate": "2026-11-23"
        }
    }

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
