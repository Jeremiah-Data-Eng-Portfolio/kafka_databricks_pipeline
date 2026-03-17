# v2: Streaming Reliability & Engagement Analytics Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Kafka](https://img.shields.io/badge/Kafka-Confluent%20Cloud-black)
![Spark](https://img.shields.io/badge/Apache%20Spark-Structured%20Streaming-E25A1C)
![Databricks](https://img.shields.io/badge/Databricks-Workflows%20%26%20Delta-FC4C02)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-Medallion-0A4ABF)
![dbt](https://img.shields.io/badge/dbt-Serving%20Layer-FF694B)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)

This version of the project focuses on how the pipeline would look if it were rebuilt with stronger production habits.

It keeps the Twitch chat streaming use case, but the emphasis is different from v1. The main goals here are cleaner medallion boundaries, safer replay behavior, explicit DLQ handling, and better operational visibility.

## Table of Contents

- [What v2 Is Meant to Show](#what-v2-is-meant-to-show)
- [Pipeline Flow](#pipeline-flow)
- [Silver Layer Responsibilities](#silver-layer-responsibilities)
- [Repository Structure](#repository-structure)
- [Runtime and Dependency Files](#runtime-and-dependency-files)
- [Kafka Configuration](#kafka-configuration)
- [Documentation](#documentation)
- [Current Limits and Future Work](#current-limits-and-future-work)

## What v2 Is Meant to Show

This version is meant to signal the following:

- Bronze, Silver, and Gold have clearer responsibilities
- Bronze stays raw and append-only
- Silver owns the parsed contract and deduplication boundary
- DLQ handling is explicit for parse failures and contract failures
- Streaming observability is treated as part of the system, not an afterthought
- Gold is framed as a stakeholder-facing data product
- Cost and operating concerns are part of the design discussion

## Pipeline Flow

The high-level flow is:

1. A Python producer captures Twitch chat events
2. Events are sent to Kafka
3. `bronze_ingest` lands the raw payload in Bronze
4. `silver_parse` reads Bronze, parses the payload, validates required fields, and deduplicates on `event_id`
5. Invalid records are written to the DLQ
6. `silver_features` reads the canonical parsed Silver output and adds lightweight message features
7. dbt builds serving-layer models for downstream analysis

In this version, the secondary enrichment consumer from v1 is not part of the main architecture. It is preserved as historical context only.

## Silver Layer Responsibilities

The Silver layer is currently split into two jobs with different responsibilities.

### `silver_parse`

`silver_parse` is the canonical contract boundary.

It does the following:

- reads from the Bronze table
- parses the raw JSON payload
- normalizes key fields such as channel, chatter, and message text
- assigns `event_id` from topic, partition, and offset
- validates required fields
- deduplicates valid records using a watermark and `dropDuplicates`
- writes invalid or unparseable records to the DLQ

This job writes to:

- `silver_parsed_table`
- `dlq_table`

### `silver_features`

`silver_features` reads from the canonical parsed Silver table and derives lightweight heuristics.

It adds fields such as:

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

This job does not own deduplication and does not currently merge back into the parsed table. It writes an append-only feature table instead.

## Repository Structure

- `src/producer/`  
  Producer code and config

- `src/streaming/jobs/`  
  Streaming job entrypoints for Bronze, Silver, and DLQ routing

- `src/streaming/schemas/`  
  Event schema definitions

- `src/streaming/transforms/`  
  Parsing, dedupe, feature engineering, and quality rules

- `src/streaming/observability/`  
  Freshness, volume, schema drift, and SLO utilities

- `src/streaming/utils/`  
  Shared config and logging helpers

- `src/dbt/`  
  dbt project for serving-layer models

- `databricks/`  
  Databricks job YAML scaffold and notes

- `docs/`  
  Architecture notes, ADRs, runbook, observability, FinOps, and related design docs

- `tests/`  
  Unit, integration, and data-quality test scaffolding

- `dashboards/`  
  Example operational metric definitions

## Runtime and Dependency Files

### `requirements.txt`

Runtime dependencies used by the Databricks jobs.

Notable entries include:

- editable install of the local package
- `kafka-python`

### `requirements-dev.txt`

Local development and test extras.

### `pyproject.toml`

Project metadata, package configuration, and pytest defaults.

## Kafka Configuration

For Confluent Cloud, the main settings are:

- `KAFKA_BOOTSTRAP_SERVERS=<cluster>.confluent.cloud:9092`
- `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
- `KAFKA_SASL_MECHANISM=PLAIN`
- `API_KEY=<confluent_api_key>`
- `API_SECRET=<confluent_api_secret>`

Other important runtime variables used by the jobs include:

- `RUN_ID` (explicit benchmark/run label attached to each landed micro-batch)
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

## Current Limits and Future Work

Current areas that still need work include:

- stronger runtime hardening around state and backpressure
- more explicit checkpoint and replay playbooks
- better integration testing with an ephemeral Kafka and Spark harness
- better observability export into dashboards
- add LLM-assisted context classification with emote-aware embedding features
