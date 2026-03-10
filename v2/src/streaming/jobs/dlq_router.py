from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from streaming.schemas.dlq_event import DlqEvent
from streaming.utils.logging import get_logger

LOGGER = get_logger("streaming.dlq_router")

FAILURE_REASONS = {
    "PARSE_ERROR": "Failed to parse raw payload as valid event envelope",
    "CONTRACT_ERROR": "Required fields missing after parse/normalize",
    "TYPE_ERROR": "Type mismatch against expected Silver contract",
    "QUALITY_ERROR": "Quality policy violation",
    "UNKNOWN_ERROR": "Unknown processing error",
}


def build_dlq_event(
    raw_payload: str,
    error_reason: str,
    retryable: bool,
    source_topic: str | None = None,
    source_partition: int | None = None,
    source_offset: int | None = None,
    error_code: str | None = None,
) -> DlqEvent:
    return DlqEvent(
        dlq_ingestion_ts=datetime.now(timezone.utc),
        error_category=error_code or "UNKNOWN_ERROR",
        error_code=error_code,
        error_detail=error_reason,
        retryable=retryable,
        raw_payload=raw_payload,
        source_topic=source_topic,
        source_partition=source_partition,
        source_offset=source_offset,
    )


def route_to_table(dlq_df: Any, table_name: str, checkpoint_location: str) -> Any:
    """Write DLQ rows to Delta sink in append mode."""

    LOGGER.info(
        "route_dlq_start",
        extra={"context": {"table": table_name, "checkpoint": checkpoint_location}},
    )
    return (
        dlq_df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_location)
        .toTable(table_name)
    )


def run(dlq_df: Any, table_name: str, checkpoint_location: str) -> Any:
    """Job-style entrypoint for wiring DLQ sink in orchestration/tests."""

    return route_to_table(dlq_df, table_name, checkpoint_location)
