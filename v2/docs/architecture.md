# Streaming Reliability & Engagement Analytics Platform

## Platform Identity

Production-oriented Twitch chat streaming pipeline using Kafka + Spark/Databricks + Delta + dbt, with medallion separation, DLQ handling, observability, and business-facing so-what metrics.

## Core Flow

1. Producer captures raw Twitch messages.
2. Kafka topic carries raw events.
3. Spark streaming writes Bronze as raw immutable Delta.
4. Invalid/parsing failures route to DLQ.
5. Silver handles parsing, normalization, type enforcement, and feature derivation.
6. Gold serves stakeholder-facing metrics.

## Explicit Scope

- Included: medallion pipeline, idempotency strategy, observability, DLQ pattern, FinOps-aware design.
- Removed from core v2 story: secondary enrichment consumer as a required architectural component.
- Historical note: the secondary consumer remains documented in `v1` as an early experiment.
