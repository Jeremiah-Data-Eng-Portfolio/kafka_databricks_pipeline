# Streaming Reliability and Engagement Analytics Pipeline

## Purpose

v2 keeps the same Twitch chat use case as the original prototype, but restructures the pipeline so the streaming boundaries are easier to reason about and benchmark.

The key design change is responsibility split:

- Bronze captures raw Kafka payloads and transport metadata only
- Silver parse owns canonical parsing, normalization, required-field validation, and deduplication
- Silver features derives lightweight heuristics from already valid Silver rows
- dbt models serve curated operational and engagement outputs downstream

## Core Flow

1. The Python producer captures Twitch chat messages and emits a JSON envelope to Kafka.
2. `bronze_ingest` reads Kafka and writes append-only Bronze rows with transport metadata.
3. `silver_parse` reads Bronze, parses the JSON payload, validates required fields, and deduplicates valid rows on `event_id` using a watermark-bounded streaming strategy.
4. Parse failures and contract-invalid rows are routed to the DLQ.
5. `silver_features` reads the canonical Silver parsed table and computes lightweight text heuristics.
6. dbt models consume curated Silver and operational tables for downstream reporting.

## Job Ownership

### Producer

Owns event capture and the producer envelope written to Kafka.

### Bronze Ingest

Owns raw capture only.

Included:

- Kafka topic, partition, offset, and timestamp
- raw payload preservation
- Bronze ingestion timestamp
- per-batch operational metadata on write

Explicitly not included:

- contract validation
- parsing and normalization
- deduplication
- feature derivation

### Silver Parse

Owns the canonical parsed contract boundary.

Included:

- JSON parsing from raw Bronze payloads
- required-field validation
- normalization of channel, chatter, and message fields
- deterministic `event_id` generation from source topic, partition, and offset
- watermark-bounded deduplication on `event_id`
- DLQ routing for parse and contract failures
- per-batch operational metrics emission

### Silver Features

Consumes contract-valid Silver rows and derives lightweight heuristics only.

Included:

- token and character-count features
- simple link, repeat-pattern, and engagement heuristics
- feature processing latency measurement
- per-batch operational metrics emission

Explicitly not included:

- contract validation
- replay ownership
- deduplication

## Canonical Contract and Operational Artifacts

The main contract boundary in v2 is the parsed Silver table.

Related artifacts:

- [`../contracts/data_contracts.yaml`](../contracts/data_contracts.yaml)
- [`streaming_observability.md`](streaming_observability.md)
- [`runbook.md`](runbook.md)
- [`finops_report.md`](finops_report.md)

The contract file documents three key tables:

- `silver_chat_parsed`
- `chat_dlq`
- `streaming_batch_metrics`

## Measured Operations

Every streaming write can stamp the following operational metadata onto output rows:

- `_run_id`
- `_job_name`
- `_batch_id`
- `_batch_processed_ts`

When `OPS_METRICS_TABLE` is configured, each micro-batch can also emit one compact benchmark row with:

- `run_id`
- `job_name`
- `batch_id`
- `batch_processed_ts`
- `row_count`
- `target_table`

This makes it possible to compare:

- batch shape across `bronze_ingest`, `silver_parse`, `silver_features`, and DLQ routing
- baseline versus stress-test runs
- measured runtime and throughput behavior alongside cost inputs

## Scope

Included in the v2 story:

- append-only Bronze ingest
- explicit parsed-contract ownership in Silver
- DLQ isolation of parse and contract failures
- lightweight feature derivation as a separate downstream streaming job
- batch-level operational metrics for benchmark and cost analysis
- dbt models for operational and engagement reporting

Not part of the main v2 architecture story:

- the earlier secondary enrichment consumer from v1
- infrastructure-grade uptime measurement
- heavy ML or LLM scoring in the streaming path
