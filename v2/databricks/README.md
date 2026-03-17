# Databricks Job Notes (Git-Based Streaming Tasks)

This folder contains templates for Databricks Jobs API / Jobs UI configuration.

## Scope

- These templates are **not** Asset Bundles.
- They model **three independent streaming jobs**:
  - Bronze ingest
  - Silver parse + DLQ routing
  - Silver feature derivation

## Why separate jobs

This matches long-running streaming operations where stages are started independently and then run concurrently.

- Bronze should be running first.
- Silver parse should start after Bronze is actively writing.
- Silver features should start after Silver parse is actively writing.

A small startup delay between jobs is expected operationally.

## File reference

- `job.yml`: copy/paste payload templates for Jobs API (`/api/2.1/jobs/create`) or equivalent Jobs UI fields.

## Required env vars

Configure these in job/task environment variables (or secret scope references):

- `APP_ENV`
- `RUN_ID` (example: `v2_baseline_real_backlog_2026_03_16`)
- `KAFKA_BOOTSTRAP_SERVERS`
- `KAFKA_RAW_TOPIC`
- `KAFKA_SECURITY_PROTOCOL` (`SASL_SSL` for Confluent Cloud)
- `KAFKA_SASL_MECHANISM` (`PLAIN` for Confluent Cloud)
- `API_KEY` (Confluent Cloud API key)
- `API_SECRET` (Confluent Cloud API secret)
- `BRONZE_TABLE`
- `SILVER_PARSED_TABLE`
- `SILVER_FEATURES_TABLE`
- `DLQ_TABLE`
- `OPS_METRICS_TABLE` (optional, per-micro-batch benchmark metrics)
- `BRONZE_CHECKPOINT`
- `SILVER_PARSE_CHECKPOINT`
- `SILVER_FEATURES_CHECKPOINT`
- `SILVER_DEDUPE_WATERMARK`

## Secret handling

Use Databricks secret scopes for sensitive values (`API_KEY`, `API_SECRET`, `TWITCH_TOKEN` if used in job runtime).
