# Medallion Design

## Bronze

Bronze is the raw landing layer.

Responsibilities:

- ingest raw Kafka payloads in append-only mode
- preserve Kafka transport metadata
- stamp Bronze ingestion time
- retain replayable source truth for downstream recovery and reprocessing

Key fields include:

- `source_topic`
- `source_partition`
- `source_offset`
- `kafka_timestamp`
- `kafka_timestamp_type`
- `raw_key`
- `raw_payload`
- `bronze_ingestion_ts`

Design notes:

- Bronze does not parse the payload
- Bronze does not enforce required fields
- Bronze does not deduplicate
- Bronze is the replay boundary for downstream Silver logic

## Silver Parse

Silver parse is the canonical contract boundary.

Responsibilities:

- parse the Bronze JSON payload into a typed event shape
- normalize channel, chatter, and message fields
- validate required fields
- derive deterministic `event_id` from topic, partition, and offset
- deduplicate valid rows using watermark-bounded streaming dedupe
- route invalid rows to the DLQ

Canonical parsed fields include:

- `event_id`
- `source_topic`
- `source_partition`
- `source_offset`
- `event_ts`
- `bronze_ingestion_ts`
- `silver_processed_ts`
- `channel`
- `chatter_id`
- `message_text`
- `message_text_normalized`
- `message_length`
- `source_platform`

Contract reference:

- [`../contracts/data_contracts.yaml`](../contracts/data_contracts.yaml)

## Silver Features

Silver features is a downstream enhancement layer built from already valid Silver parsed rows.

Responsibilities:

- consume `silver_chat_parsed`
- derive lightweight message heuristics
- write a separate append-only feature table
- avoid ownership of parsing, contract enforcement, or deduplication

Representative feature outputs include:

- `token_count`
- `alpha_char_count`
- `numeric_char_count`
- `link_count`
- `candidate_emote_token_count`
- `repeat_char_ratio`
- `text_complexity_proxy`
- `event_to_feature_latency_seconds`
- `has_repeat_spam_pattern`
- `engagement_signal`
- `feature_processed_ts`

## DLQ

The DLQ captures rows that fail parsing or contract validation.

Stored context includes:

- `dlq_ingestion_ts`
- `error_category`
- `error_code`
- `error_detail`
- `retryable`
- `raw_payload`
- `source_topic`
- `source_partition`
- `source_offset`
- `source_event_ts`
- `pipeline_stage`

Design notes:

- parse failures and contract failures are isolated from the canonical Silver table
- DLQ is intentionally append-only for triage and replay workflows
- DLQ is not deduplicated because failure volume itself is an operational signal

## Operational Metadata

Streaming writes can append the following metadata columns to written tables:

- `_run_id`
- `_job_name`
- `_batch_id`
- `_batch_processed_ts`

The pipeline can also emit one compact operational row per micro-batch into `streaming_batch_metrics` for benchmark and cost analysis.

## Gold and Serving Layer

Downstream dbt models serve two broad purposes:

- engagement reporting built from curated Silver outputs
- operational reporting built from DLQ and streaming batch metrics

This keeps Gold and serving logic separate from streaming ingestion concerns while still allowing the repository to expose both business-facing and operational views of the pipeline.