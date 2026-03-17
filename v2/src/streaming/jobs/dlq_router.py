from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from streaming.schemas.dlq_event import DlqEvent
from streaming.utils.batch_writes import stream_append_with_batch_metadata
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


def route_to_table(
    dlq_df: Any,
    table_name: str,
    checkpoint_location: str,
    trigger_available_now: bool = False,
    run_id: str | None = None,
    job_name: str = "dlq_router",
) -> Any:
    """Write DLQ rows to Delta sink in append mode."""

    LOGGER.info(
        "route_dlq_start",
        extra={
            "context": {
                "table": table_name,
                "checkpoint": checkpoint_location,
                "trigger_available_now": trigger_available_now,
                "batch_metadata_enabled": bool(run_id),
                "job_name": job_name,
            }
        },
    )
    if run_id:
        return stream_append_with_batch_metadata(
            stream_df=dlq_df,
            target_table=table_name,
            checkpoint_location=checkpoint_location,
            run_id=run_id,
            job_name=job_name,
            available_now=trigger_available_now,
        )
    writer = (
        dlq_df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_location)
    )
    if trigger_available_now:
        writer = writer.trigger(availableNow=True)
    return writer.toTable(table_name)


def run(
    dlq_df: Any,
    table_name: str,
    checkpoint_location: str,
    trigger_available_now: bool = False,
    run_id: str | None = None,
    job_name: str = "dlq_router",
) -> Any:
    """Job-style entrypoint for wiring DLQ sink in orchestration/tests."""

    return route_to_table(
        dlq_df=dlq_df,
        table_name=table_name,
        checkpoint_location=checkpoint_location,
        trigger_available_now=trigger_available_now,
        run_id=run_id,
        job_name=job_name,
    )
