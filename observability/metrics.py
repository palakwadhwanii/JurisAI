import time
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    REGISTRY,
    generate_latest,
    CONTENT_TYPE_LATEST
)

# ==============================================================================
# PHASE 17 PROMETHEUS METRICS DEFINITIONS
# ==============================================================================

# 1. API Request Tracking
API_REQUESTS_TOTAL = Counter(
    "jurisai_api_requests_total",
    "Total HTTP API requests processed by JurisAI",
    ["method", "endpoint", "status_code"]
)

API_REQUEST_DURATION_SECONDS = Histogram(
    "jurisai_api_request_duration_seconds",
    "HTTP API response latency distribution in seconds",
    ["method", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

# 2. Case Analyses Outcomes
CASE_ANALYSIS_TOTAL = Counter(
    "jurisai_case_analyses_total",
    "Total legal case analyses completed",
    ["outcome", "case_type"]
)

CASE_ANALYSIS_DURATION_SECONDS = Histogram(
    "jurisai_case_analysis_duration_seconds",
    "Total pipeline execution duration per case analysis in seconds",
    ["outcome"],
    buckets=[0.5, 1.0, 2.0, 3.5, 5.0, 7.5, 10.0, 15.0, 30.0]
)

# 3. Agent Execution & Failure Tracking
AGENT_EXECUTION_DURATION_SECONDS = Histogram(
    "jurisai_agent_execution_duration_seconds",
    "Execution duration by specific agent in seconds",
    ["agent_name", "status"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

AGENT_FAILURES_TOTAL = Counter(
    "jurisai_agent_failures_total",
    "Total failures, exceptions, or unhandled errors encountered by agents",
    ["agent_name", "error_type"]
)

# 4. RAG Latency & Retrieval Tracking
RAG_RETRIEVAL_DURATION_SECONDS = Histogram(
    "jurisai_rag_retrieval_duration_seconds",
    "Vector search latency in ChromaDB in seconds",
    ["collection_name"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

RAG_RETRIEVED_DOCUMENTS_COUNT = Histogram(
    "jurisai_rag_retrieved_documents_count",
    "Number of chunks retrieved per query",
    ["collection_name"],
    buckets=[0, 1, 2, 4, 6, 8, 12, 16, 25]
)

RAG_RETRIEVAL_FAILURES_TOTAL = Counter(
    "jurisai_rag_retrieval_failures_total",
    "Total empty or failed RAG retrievals",
    ["collection_name", "reason"]
)

# 5. Auditor & Self-Correction Re-analysis Tracking
AUDIT_RESULTS_TOTAL = Counter(
    "jurisai_audit_results_total",
    "Total audit verdicts rendered by AuditorAgent",
    ["audit_status"]  # PASS, WARN, FAIL, INSUFFICIENT_INPUT
)

REANALYSIS_ITERATIONS_TOTAL = Counter(
    "jurisai_reanalysis_iterations_total",
    "Total targeted re-analysis cycles executed by ReanalysisRouter",
    ["target_agent"]
)

REANALYSIS_LOOPS_PER_CASE = Histogram(
    "jurisai_reanalysis_loops_per_case",
    "Number of iterative loops required per case before final report",
    buckets=[1, 2, 3, 4, 5]
)

# 6. Local LLM / External API Failures
LLM_FAILURES_TOTAL = Counter(
    "jurisai_llm_failures_total",
    "Total failures or timeouts contacting local Ollama or external models",
    ["model_name", "reason"]
)

# Active Analyses In-Flight Gauge
ACTIVE_ANALYSES_GAUGE = Gauge(
    "jurisai_active_analyses_in_flight",
    "Number of case analyses currently executing"
)


# ==============================================================================
# CONTEXT MANAGERS & HELPER RECORDERS
# ==============================================================================

class AgentTimer:
    """Context manager to measure and record an agent execution."""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.start_time: float = 0.0
        self.duration: float = 0.0
        self.status: str = "SUCCESS"

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.perf_counter() - self.start_time
        if exc_type is not None:
            self.status = "ERROR"
            AGENT_FAILURES_TOTAL.labels(
                agent_name=self.agent_name,
                error_type=exc_type.__name__
            ).inc()
        AGENT_EXECUTION_DURATION_SECONDS.labels(
            agent_name=self.agent_name,
            status=self.status
        ).observe(self.duration)
        return False  # Do not suppress exception


def record_rag_retrieval(collection_name: str, duration: float, doc_count: int, failed: bool = False, reason: str = ""):
    """Records RAG latency, retrieved document count, and failure flags."""
    RAG_RETRIEVAL_DURATION_SECONDS.labels(collection_name=collection_name).observe(duration)
    RAG_RETRIEVED_DOCUMENTS_COUNT.labels(collection_name=collection_name).observe(doc_count)
    if failed or doc_count == 0:
        RAG_RETRIEVAL_FAILURES_TOTAL.labels(
            collection_name=collection_name,
            reason=reason or ("zero_documents" if doc_count == 0 else "exception")
        ).inc()


def get_prometheus_metrics() -> bytes:
    """Returns serialized Prometheus metrics in text format."""
    return generate_latest(REGISTRY)
