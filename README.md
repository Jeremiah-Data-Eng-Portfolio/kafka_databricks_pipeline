# Streaming Reliability & Engagement Analytics Platform

This repository is a two-version portfolio case study for Twitch chat analytics:

- `v1/prototype`: original working prototype, preserved.
- `v2`: production-oriented architecture emphasizing reliability, data quality, observability, FinOps, and business metrics.

## Platform Definition

A production-oriented Twitch chat streaming pipeline using Kafka + Spark/Databricks + Delta + dbt, with medallion separation, DLQ handling, observability, and business-facing so-what metrics.

## Repository Layout

- `v1/`: preserved prototype artifacts.
- `v2/`: production-style source organization and operational docs.

## v1 vs v2

### v1 (prototype)

- Demonstrates end-to-end pipeline feasibility.
- Contains original ingestion scripts, dbt marts, and architecture images.

### v2 (production-oriented)

- Explicit Bronze/Silver/Gold boundaries.
- Raw immutable ingest + idempotent key strategy.
- DLQ design and observability modules.
- Stakeholder-facing Gold metrics framing.
- FinOps and AI-readiness documentation.

## Start Here

1. Prototype path: [`v1/prototype/README.md`](v1/prototype/README.md)
2. Production path: [`v2/README.md`](v2/README.md)
