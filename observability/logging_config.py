import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Context variable to hold analysis_id across threads and async contexts
current_analysis_id: ContextVar[str] = ContextVar("current_analysis_id", default="system")

class StructuredJsonFormatter(logging.Formatter):
    """
    JSON Formatter enforcing structured log output with required Phase 17 fields:
    - analysis_id
    - agent_name
    - timestamp (ISO-8601 UTC)
    - status
    - duration (seconds)
    - message and additional extra fields
    """
    def format(self, record: logging.LogRecord) -> str:
        log_time = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        
        # Extract analysis_id: from record.__dict__, then contextvar, then 'system'
        analysis_id = getattr(record, "analysis_id", None) or current_analysis_id.get("system")
        agent_name = getattr(record, "agent_name", "JurisAISystem")
        status = getattr(record, "status", record.levelname)
        duration = getattr(record, "duration", None)
        
        log_obj: Dict[str, Any] = {
            "timestamp": log_time,
            "analysis_id": str(analysis_id),
            "agent_name": str(agent_name),
            "status": str(status),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        if duration is not None:
            try:
                log_obj["duration"] = round(float(duration), 4)
            except (ValueError, TypeError):
                log_obj["duration"] = duration

        # Add optional RAG and analysis metrics if passed in extra
        for optional_key in [
            "latency", "doc_count", "iteration", "audit_status", 
            "error_type", "case_type", "reanalysis_required", "endpoint"
        ]:
            if hasattr(record, optional_key):
                val = getattr(record, optional_key)
                if val is not None:
                    log_obj[optional_key] = val

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def setup_logging(log_file: Optional[Path] = None, log_level: int = logging.INFO) -> logging.Logger:
    """
    Configures application-wide structured JSON logging to stderr and an optional file.
    """
    root_logger = logging.getLogger("jurisai")
    root_logger.setLevel(log_level)
    root_logger.propagate = False

    # Clear existing handlers to prevent duplication on reload
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = StructuredJsonFormatter()

    # Stream Handler (stdout / console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    root_logger.addHandler(stream_handler)

    # Optional File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    return root_logger

# Default singleton logger
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
DEFAULT_LOG_FILE = LOG_DIR / "jurisai_app.log"
logger = setup_logging(log_file=DEFAULT_LOG_FILE)

def get_logger(name: str = "jurisai") -> logging.Logger:
    child = logging.getLogger(f"jurisai.{name}")
    child.setLevel(logging.INFO)
    child.propagate = True
    return child
