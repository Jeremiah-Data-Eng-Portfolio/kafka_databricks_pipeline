from __future__ import annotations

from typing import Any

from streaming.jobs.dlq_router import route_to_table
from streaming.utils.batch_writes import stream_append_with_batch_metadata
from streaming.utils.config_loader import StreamingJobConfig, load_streaming_config
from streaming.utils.logging import get_logger

LOGGER = get_logger("streaming.silver_parse")


def _envelope_schema() -> Any:
    from pyspark.sql.types import StringType, StructField, StructType

    return StructType(
        [
            StructField("ingestion_ts", StringType(), True),
            StructField(
                "source",
                StructType(
                    [
                        StructField("platform", StringType(), True),
                        StructField("protocol", StringType(), True),
                        StructField("server", StringType(), True),
                        StructField("channel", StringType(), True),
                    ]
                ),
                True,
            ),
            StructField(
                "raw",
                StructType(
                    [
                        StructField("irc_line", StringType(), True),
                        StructField("username", StringType(), True),
                        StructField("message", StringType(), True),
                    ]
                ),
                True,
            ),
            StructField(
                "metadata",
                StructType(
                    [
                        StructField("event_kind", StringType(), True),
                        StructField("producer_env", StringType(), True),
                        StructField("schema_version", StringType(), True),
                    ]
                ),
                True,
            ),
        ]
    )


def _blank_to_null(value_col: Any, lower: bool = False) -> Any:
    from pyspark.sql import functions as F

    cleaned = F.trim(value_col)
    normalized = F.lower(cleaned) if lower else cleaned
    return F.when(F.length(normalized) == 0, F.lit(None)).otherwise(normalized)


def build_parsed_and_dlq_dataframes(spark: Any, cfg: StreamingJobConfig) -> tuple[Any, Any]:
    """Build canonical Silver parsed stream + DLQ stream.

    Design notes:
    - Bronze remains raw append-only.
    - Silver is the canonical parsed contract boundary.
    - Canonical dedupe is enforced in Silver on event_id.
    - Watermark bounds state for scalable streaming dedupe.
    """

    from pyspark.sql import functions as F

    bronze_df = spark.readStream.table(cfg.bronze_table)
    parsed_envelope = bronze_df.withColumn("envelope", F.from_json(F.col("raw_payload"), _envelope_schema()))

    # Parse failures are isolated first so they cannot leak into contract validation.
    parseable_df = parsed_envelope.filter(F.col("envelope").isNotNull())
    parse_failures_df = parsed_envelope.filter(F.col("envelope").isNull())
    channel_norm = _blank_to_null(F.col("envelope.source.channel"), lower=True)
    chatter_norm = _blank_to_null(F.col("envelope.raw.username"), lower=True)
    message_norm = _blank_to_null(F.col("envelope.raw.message"), lower=False)
    message_norm_lower = _blank_to_null(F.col("envelope.raw.message"), lower=True)
    source_platform_norm = _blank_to_null(F.col("envelope.source.platform"), lower=True)

    parsed = parseable_df.select(
        F.concat_ws(":", F.col("source_topic"), F.col("source_partition"), F.col("source_offset")).alias("event_id"),
        F.col("source_topic"),
        F.col("source_partition"),
        F.col("source_offset"),
        F.col("kafka_timestamp").cast("timestamp").alias("event_ts"),
        F.col("bronze_ingestion_ts"),
        F.current_timestamp().alias("silver_processed_ts"),
        channel_norm.alias("channel"),
        chatter_norm.alias("chatter_id"),
        message_norm.alias("message_text"),
        message_norm_lower.alias("message_text_normalized"),
        F.length(message_norm).cast("int").alias("message_length"),
        F.coalesce(source_platform_norm, F.lit("twitch")).alias("source_platform"),
        F.col("raw_payload"),
    )

    valid_base = parsed.filter(
        F.col("channel").isNotNull()
        & F.col("chatter_id").isNotNull()
        & F.col("message_text").isNotNull()
        & (F.col("message_length") > 0)
    ).drop("raw_payload")
    # Canonical streaming dedupe in Silver on event_id with bounded state.
    valid = valid_base.withWatermark("event_ts", cfg.silver_dedupe_watermark).dropDuplicates(["event_id"])

    invalid = parsed.filter(
        F.col("channel").isNull()
        | F.col("chatter_id").isNull()
        | F.col("message_text").isNull()
        | (F.col("message_length") <= 0)
    ).select(
        F.current_timestamp().alias("dlq_ingestion_ts"),
        F.lit("CONTRACT_ERROR").alias("error_category"),
        F.lit("CONTRACT_REQUIRED_FIELDS_MISSING").alias("error_code"),
        F.lit("Required parsed fields missing or invalid").alias("error_detail"),
        F.lit(False).alias("retryable"),
        F.col("raw_payload"),
        F.col("source_topic"),
        F.col("source_partition"),
        F.col("source_offset"),
        F.col("event_ts").alias("source_event_ts"),
        F.lit("silver_parse").alias("pipeline_stage"),
    )

    parse_failures = parse_failures_df.select(
        F.current_timestamp().alias("dlq_ingestion_ts"),
        F.lit("PARSE_ERROR").alias("error_category"),
        F.lit("JSON_PARSE_FAILURE").alias("error_code"),
        F.lit("Raw payload could not be parsed").alias("error_detail"),
        # Treat parse failures as retryable for replay workflows after parser/schema fixes.
        F.lit(True).alias("retryable"),
        F.col("raw_payload"),
        F.col("source_topic"),
        F.col("source_partition"),
        F.col("source_offset"),
        F.col("kafka_timestamp").alias("source_event_ts"),
        F.lit("silver_parse").alias("pipeline_stage"),
    )

    # DLQ intentionally keeps full failure stream for triage; canonical dedupe is only for valid Silver rows.
    dlq = parse_failures.unionByName(invalid)
    return valid, dlq


def run(spark: Any | None = None) -> tuple[Any, Any]:
    cfg = load_streaming_config()

    if spark is None:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("v2_silver_parse").getOrCreate()

    valid_df, dlq_df = build_parsed_and_dlq_dataframes(spark, cfg)

    LOGGER.info(
        "silver_parse_start",
        extra={
            "context": {
                "silver_table": cfg.silver_parsed_table,
                "dlq_table": cfg.dlq_table,
                "silver_dedupe_watermark": cfg.silver_dedupe_watermark,
                "run_id": cfg.run_id,
                "ops_metrics_table": cfg.ops_metrics_table or None,
            }
        },
    )

    silver_query = stream_append_with_batch_metadata(
        stream_df=valid_df,
        target_table=cfg.silver_parsed_table,
        checkpoint_location=cfg.silver_parse_checkpoint,
        run_id=cfg.run_id,
        job_name="silver_parse",
        ops_metrics_table=cfg.ops_metrics_table or None,
        available_now=True,
    )

    dlq_query = route_to_table(
        dlq_df=dlq_df,
        table_name=cfg.dlq_table,
        checkpoint_location=f"{cfg.silver_parse_checkpoint}_dlq",
        trigger_available_now=True,
        run_id=cfg.run_id,
        job_name="silver_parse",
        ops_metrics_table=cfg.ops_metrics_table or None,
    )
    return silver_query, dlq_query
