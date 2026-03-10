# ADR 0004: Measure Freshness, Volume, and Schema Drift

## Status
Accepted

## Context
Operational confidence in streaming pipelines cannot rely on job-success status alone; it requires timely, volumetric, and contract-health signals.

## Decision
Define core observability around three pillars: freshness (latency/lag), volume (throughput and anomalies), and schema drift (required/type/unexpected field checks).

## Consequences
- Improves detection of silent degradation and upstream contract issues.
- Supports clearer runbook actions and SLO-oriented operations.
- Adds metric instrumentation and dashboard maintenance overhead.
