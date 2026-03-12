from __future__ import annotations

from typing import Any

from streaming.utils.config_loader import StreamingJobConfig, load_streaming_config
from streaming.utils.logging import get_logger

LOGGER = get_logger("streaming.bronze_ingest")


def build_bronze_dataframe(spark: Any, cfg: StreamingJobConfig) -> Any:
    """Read Kafka raw events and prepare append-only Bronze rows.

    Bronze is intentionally raw and immutable in v2:
    - no parse/contract enforcement
    - no dedupe/merge
    - preserve source payload + Kafka coordinates for downstream replayability
    """

    from pyspark.sql import functions as F

    reader = spark.readStream.format("kafka")
    for key, value in cfg.kafka_read_options().items():
        reader = reader.option(key, value)
    kafka_stream = reader.load()

    # Keep Bronze as close to source truth as possible.
    return kafka_stream.select(
        F.col("topic").alias("source_topic"),
        F.col("partition").cast("int").alias("source_partition"),
        F.col("offset").cast("long").alias("source_offset"),
        F.col("timestamp").alias("kafka_timestamp"),
        F.col("timestampType").cast("int").alias("kafka_timestamp_type"),
        F.col("key").cast("string").alias("raw_key"),
        F.col("value").cast("string").alias("raw_payload"),
        F.current_timestamp().alias("bronze_ingestion_ts"),
    )


def run(spark: Any | None = None) -> Any:
    """Start append-only Bronze sink.

    Canonical contract enforcement and dedupe are intentionally downstream responsibilities
    in `silver_parse`.
    """

    cfg = load_streaming_config()

    if spark is None:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("v2_bronze_ingest").getOrCreate()

    bronze_df = build_bronze_dataframe(spark, cfg)

    LOGGER.info(
        "bronze_stream_start",
        extra={"context": {"table": cfg.bronze_table, "append_only_raw": True}},
    )
    return (
        bronze_df.writeStream.format("delta")
        .trigger(availableNow=True)
        .outputMode("append")
        .option("checkpointLocation", cfg.bronze_checkpoint)
        .toTable(cfg.bronze_table)
    )
