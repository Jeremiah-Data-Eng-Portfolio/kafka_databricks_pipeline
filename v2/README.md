# v2: Streaming Reliability and Engagement Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Kafka](https://img.shields.io/badge/Kafka-Confluent%20Cloud-black)
![Spark](https://img.shields.io/badge/Apache%20Spark-Structured%20Streaming-E25A1C)
![Databricks](https://img.shields.io/badge/Databricks-Workflows%20%26%20Delta-FC4C02)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-Medallion-0A4ABF)
![dbt](https://img.shields.io/badge/dbt-Serving%20Layer-FF694B)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)

This version of the project rebuilds the original Twitch chat pipeline with clearer streaming boundaries and a more defensible medallion design.

The focus of v2 is not adding more features than v1. The focus is making the pipeline easier to reason about operationally: Bronze stays raw, Silver owns parsing and contract enforcement, DLQ handling is explicit, and downstream analytics are built from curated outputs rather than mixed responsibilities.

## Table of Contents

- [What Changed in v2](#what-changed-in-v2)
- [Pipeline Overview](#pipeline-overview)
- [Layer Responsibilities](#layer-responsibilities)
- [Repository Structure](#repository-structure)
- [Runtime and Dependency Files](#runtime-and-dependency-files)
- [Kafka and Job Configuration](#kafka-and-job-configuration)
- [Documentation](#documentation)
- [Current Scope](#current-scope)
- [Planned Next Steps](#planned-next-steps)

## What Changed in v2

Compared with v1, this version emphasizes:

- clearer Bronze, Silver, and Gold responsibilities
- append-only raw Bronze ingest
- Silver as the canonical parsed contract boundary
- explicit DLQ routing for malformed or invalid records
- separate feature derivation from parsing and deduplication logic
- a cleaner story for replay, auditability, and downstream modeling

The earlier secondary enrichment consumer is not part of the main v2 architecture. It is preserved as historical context from v1 only.

## Pipeline Overview

The current end-to-end flow is:

1. A Python producer captures Twitch chat events
2. Events are sent to Kafka
3. `bronze_ingest` writes the raw payload into a Bronze Delta table
4. `silver_parse` reads Bronze, parses the payload, validates required fields, assigns `event_id`, and deduplicates valid records
5. Invalid or unparseable records are written to a DLQ table
6. `silver_features` reads the canonical parsed Silver output and derives lightweight message features
7. dbt builds serving-layer models for downstream analysis

## Layer Responsibilities

### Bronze

`bronze_ingest` is responsible for raw capture only.

Current responsibilities:

- read from Kafka
- preserve the raw event payload
- record ingestion metadata
- write append-only records into Bronze

Bronze does not enforce the parsed contract and does not perform deduplication.

### Silver Parse

`silver_parse` is the canonical parsing and validation boundary.

Current responsibilities:

- read raw Bronze records
- parse the raw JSON payload
- normalize key fields such as channel, chatter, and message text
- assign `event_id` from topic, partition, and offset
- validate required fields
- deduplicate valid records with watermark-bounded `dropDuplicates`
- route invalid or unparseable records to the DLQ

Current outputs:

- `silver_parsed_table`
- `dlq_table`

### Silver Features

`silver_features` reads the canonical parsed Silver output and derives lightweight message-level features.

Current responsibilities:

- read from `silver_parsed_table`
- add heuristic text features
- write a separate append-only features table

This job does not own parsing, contract enforcement, or deduplication.

Current derived fields include:

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

## Repository Structure

- `src/producer/`  
  Producer code and configuration

- `src/streaming/jobs/`  
  Streaming job entrypoints for Bronze ingest, Silver parsing, feature derivation, and DLQ routing

- `src/streaming/schemas/`  
  Event schema definitions

- `src/streaming/transforms/`  
  Parsing, deduplication, feature engineering, and quality logic

- `src/streaming/observability/`  
  Helper utilities for freshness, volume, schema drift, and related checks

- `src/streaming/utils/`  
  Shared config and logging helpers

- `src/dbt/`  
  dbt project for serving-layer models

- `databricks/`  
  Databricks job YAML scaffold and setup notes

- `docs/`  
  Architecture notes, ADRs, runbook, observability notes, and related design docs

- `tests/`  
  Unit, integration, and data quality test scaffolding

- `dashboards/`  
  Example operational metric definitions

## Runtime and Dependency Files

### `requirements.txt`

Runtime dependencies used by the Databricks jobs.

Notable entries include:

- editable install of the local package
- `kafka-python`

### `requirements-dev.txt`

Local development and test dependencies.

### `pyproject.toml`

Project metadata, package configuration, and pytest defaults.

## Kafka and Job Configuration

For Confluent Cloud, the main Kafka settings are:

- `KAFKA_BOOTSTRAP_SERVERS=<cluster>.confluent.cloud:9092`
- `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
- `KAFKA_SASL_MECHANISM=PLAIN`
- `API_KEY=<confluent_api_key>`
- `API_SECRET=<confluent_api_secret>`

Other important runtime variables include:

- `KAFKA_RAW_TOPIC`
- `BRONZE_TABLE`
- `SILVER_PARSED_TABLE`
- `SILVER_FEATURES_TABLE`
- `DLQ_TABLE`
- `BRONZE_CHECKPOINT`
- `SILVER_PARSE_CHECKPOINT`
- `SILVER_FEATURES_CHECKPOINT`
- `SILVER_DEDUPE_WATERMARK`

See `.env.example` and `databricks/README.md` for the full setup pattern.

## Documentation

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/medallion_design.md`](docs/medallion_design.md)
- [`docs/streaming_observability.md`](docs/streaming_observability.md)
- [`docs/runbook.md`](docs/runbook.md)
- [`docs/finops_report.md`](docs/finops_report.md)
- [`docs/so_what_metrics.md`](docs/so_what_metrics.md)
- [`docs/future_ai_readiness.md`](docs/future_ai_readiness.md)
- [`docs/adrs`](docs/adrs)

## Current Scope

What is implemented today:

- raw Twitch chat ingestion into Kafka
- append-only Bronze ingest into Delta
- Silver parsing, validation, and deduplication
- explicit DLQ routing for malformed or invalid records
- separate Silver feature derivation job
- dbt serving-layer models on top of curated outputs
- supporting design docs, ADRs, and runbook material

What is not yet fully implemented or benchmarked:

- detailed runtime benchmarking across the streaming jobs
- batch-level metric comparison between v1 and v2
- synthetic scale testing for higher throughput and burst scenarios
- systematic malformed-record injection for DLQ stress testing
- cost analysis grounded in measured run data
- stronger operational dashboards fed from job-level metrics

## Planned Next Steps

The next phase of the project is intended to make the operational claims more measurable.

Planned work includes:

- collecting benchmark metrics across `bronze_ingest`, `silver_parse`, and `silver_features`
- adding `batch_id` to support batch-level runtime and throughput analysis
- generating synthetic data to test higher-volume and burst-heavy workloads
- simulating malformed records to validate DLQ routing under stress
- comparing v1 and v2 processing behavior using measured runtime and cost inputs
- expanding observability outputs into more concrete reliability reporting