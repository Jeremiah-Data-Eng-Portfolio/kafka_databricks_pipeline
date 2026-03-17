from __future__ import annotations

from typing import Any


def append_with_batch_metadata(
    batch_df: Any,
    batch_id: int,
    target_table: str,
    run_id: str,
    job_name: str,
) -> None:
    """Append one micro-batch with run/job metadata for observability baselining."""

    from pyspark.sql import functions as F

    (
        batch_df.withColumn("_run_id", F.lit(run_id))
        .withColumn("_job_name", F.lit(job_name))
        .withColumn("_batch_id", F.lit(int(batch_id)).cast("long"))
        .withColumn("_batch_processed_ts", F.current_timestamp())
        .write.format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(target_table)
    )


def stream_append_with_batch_metadata(
    stream_df: Any,
    target_table: str,
    checkpoint_location: str,
    run_id: str,
    job_name: str,
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
        )

    writer = (
        stream_df.writeStream.outputMode("append")
        .option("checkpointLocation", checkpoint_location)
        .foreachBatch(_write_batch)
    )
    if available_now:
        writer = writer.trigger(availableNow=True)
    return writer.start()
