# v2: Streaming Reliability & Engagement Analytics Platform

A production-oriented Twitch chat streaming pipeline using Kafka + Spark/Databricks + Delta + dbt, with medallion separation, DLQ handling, observability, and business-facing so-what metrics.

## What v2 Signals

- Clean Bronze/Silver/Gold boundaries.
- Raw immutable ingest design.
- Replay/idempotency awareness (`topic + partition + offset`).
- Streaming observability (freshness, volume, schema drift).
- DLQ strategy for malformed/invalid events.
- Pipeline uptime proxy KPI for operational reliability tracking.
- FinOps-aware architecture decisions.
- Stakeholder-facing metrics rather than only technical outputs.
- Future AI-readiness foundations.

## Core Architecture

1. Producer captures raw Twitch messages.
2. Kafka topic carries raw events.
3. Spark streaming writes Bronze raw immutable.
4. Invalid/parsing failures route to DLQ.
5. Silver handles parsing, normalization, type enforcement, and feature derivation.
6. Gold serves stakeholder metrics.

Secondary enrichment consumer is not part of the v2 core architecture; it is retained as v1 historical context only.

## Canonicality Ownership

- Bronze (`bronze_ingest`): append-only raw capture, no contract enforcement or dedupe.
- Silver parse (`silver_parse`): canonical contract boundary plus canonical dedupe on `event_id` using watermark-bounded streaming dedupe.
- Silver features (`silver_features`): consumes canonical Silver parse output and computes lightweight heuristics only (no dedupe responsibility).

## v2 Structure

- `src/producer/`: producer scaffold and config.
- `src/streaming/jobs/`: bronze/silver/dlq job entrypoints.
- `src/streaming/schemas/`: typed event contracts.
- `src/streaming/transforms/`: parsing, feature engineering, quality, dedupe logic.
- `src/streaming/observability/`: freshness, volume, drift, and SLO utilities.
- `src/streaming/utils/`: shared logging/config helpers.
- `src/dbt/`: dbt project for serving-layer models.
- `databricks/`: YAML scaffolds for Git-based Databricks job/task configuration.
- `docs/`: architecture, runbook, medallion, observability, FinOps, so-what metrics, AI-readiness, ADRs.
- `tests/`: unit, integration, and data-quality scaffolding.
- `dashboards/`: sample operational metric definitions.

## Dependency Files

- `requirements.txt`: runtime dependencies for Databricks job tasks.
- `requirements-dev.txt`: local test/lint/type-check extras.
- `pyproject.toml`: package metadata and pytest defaults.

## Confluent Cloud Kafka Settings

For Confluent Cloud, configure:

- `KAFKA_BOOTSTRAP_SERVERS=<cluster>.confluent.cloud:9092`
- `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
- `KAFKA_SASL_MECHANISM=PLAIN`
- `API_KEY=<confluent_api_key>`
- `API_SECRET=<confluent_api_secret>`

## Documentation Index

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/medallion_design.md`](docs/medallion_design.md)
- [`docs/streaming_observability.md`](docs/streaming_observability.md)
- [`docs/runbook.md`](docs/runbook.md)
- [`docs/finops_report.md`](docs/finops_report.md)
- [`docs/so_what_metrics.md`](docs/so_what_metrics.md)
- [`docs/future_ai_readiness.md`](docs/future_ai_readiness.md)
- [`docs/adrs`](docs/adrs)

## TODO / Future Work

- Harden stream runtime with explicit watermarking, state metrics export, and backpressure alerting.
- Add checkpoint strategy + replay playbooks per environment.
- Add integration tests with ephemeral Kafka/Spark test harness.
- Add warehouse-level observability export to dashboards.
- Add hybrid toxicity pipeline: rules + LLM-assisted context classification with emote-aware embedding features.
