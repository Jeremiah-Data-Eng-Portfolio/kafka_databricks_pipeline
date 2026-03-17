from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _write_ops_metrics_row(
    batch_df: Any,
    ops_metrics_table: str,
    run_id: str,
    job_name: str,
    batch_id: int,
    batch_processed_ts: datetime,
    row_count: int,
    target_table: str,
) -> None:
    spark = batch_df.sparkSession
    metrics_row = [
        {
            "run_id": run_id,
            "job_name": job_name,
            "batch_id": int(batch_id),
            "batch_processed_ts": batch_processed_ts,
            "row_count": int(row_count),
            "target_table": target_table,
        }
    ]
    (
        spark.createDataFrame(metrics_row)
        .write.format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(ops_metrics_table)
    )


def append_with_batch_metadata(
    batch_df: Any,
    batch_id: int,
    target_table: str,
    run_id: str,
    job_name: str,
    ops_metrics_table: str | None = None,
) -> None:
    """Append one micro-batch with run/job metadata for observability baselining.

    If `ops_metrics_table` is provided, writes one compact benchmark row per batch:
    run_id, job_name, batch_id, batch_processed_ts, row_count, and target_table.
    """

    from pyspark.sql import functions as F
    from pyspark.storagelevel import StorageLevel

    batch_processed_ts = datetime.now(timezone.utc)
    enriched_batch_df = (
        batch_df.withColumn("_run_id", F.lit(run_id))
        .withColumn("_job_name", F.lit(job_name))
        .withColumn("_batch_id", F.lit(int(batch_id)).cast("long"))
        .withColumn("_batch_processed_ts", F.lit(batch_processed_ts).cast("timestamp"))
    )
    cached_batch_df = enriched_batch_df.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        row_count = int(cached_batch_df.count())
        (
            cached_batch_df
            .write.format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(target_table)
        )
        if ops_metrics_table:
            _write_ops_metrics_row(
                batch_df=batch_df,
                ops_metrics_table=ops_metrics_table,
                run_id=run_id,
                job_name=job_name,
                batch_id=int(batch_id),
                batch_processed_ts=batch_processed_ts,
                row_count=row_count,
                target_table=target_table,
            )
    finally:
        cached_batch_df.unpersist()


def stream_append_with_batch_metadata(
    stream_df: Any,
    target_table: str,
    checkpoint_location: str,
    run_id: str,
    job_name: str,
    ops_metrics_table: str | None = None,
    available_now: bool = True,
) -> Any:
    """Start a streaming query that appends micro-batches with observability metadata."""

    def _write_batch(batch_df: Any, batch_id: int) -> None:
        append_with_batch_metadata(
            batch_df=batch_df,
            batch_id=batch_id,
            target_table=target_table,
            run_id=run_id,
            job_name=job_name,
            ops_metrics_table=ops_metrics_table,
        )

    writer = (
        stream_df.writeStream.outputMode("append")
        .option("checkpointLocation", checkpoint_location)
        .foreachBatch(_write_batch)
    )
    if available_now:
        writer = writer.trigger(availableNow=True)
    return writer.start()
