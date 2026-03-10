from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

DLQ_ERROR_CATEGORIES = {
    "PARSE_ERROR",
    "CONTRACT_ERROR",
    "TYPE_ERROR",
    "QUALITY_ERROR",
    "UNKNOWN_ERROR",
}


@dataclass(frozen=True)
class DlqEvent:
    dlq_ingestion_ts: datetime
    error_category: str
    error_code: str | None
    error_detail: str
    retryable: bool
    raw_payload: str
    source_topic: str | None = None
    source_partition: int | None = None
    source_offset: int | None = None
    source_event_ts: datetime | None = None
    pipeline_stage: str = "silver_parse"

    @property
    def error_reason(self) -> str:
        return self.error_detail


def dlq_schema_definition() -> dict:
    """Operational DLQ schema optimized for triage and replay."""

    return {
        "dlq_ingestion_ts": "timestamp",
        "error_category": "string",
        "error_code": "string",
        "error_detail": "string",
        "retryable": "boolean",
        "raw_payload": "string",
        "source_topic": "string",
        "source_partition": "int",
        "source_offset": "long",
        "source_event_ts": "timestamp",
        "pipeline_stage": "string",
    }
