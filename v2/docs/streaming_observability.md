# Streaming Observability

## Pillar 1: Freshness

Metrics:

- Event-time to ingest lag (`event_time_to_ingest_lag_seconds`).
- Bronze-to-Silver latency (`bronze_to_silver_latency_seconds`).
- Last successful micro-batch age (`last_successful_batch_age_seconds`).

Operational interpretation:

- Rising lag indicates backlog or downstream bottleneck.
- Breached freshness thresholds should page on-call and trigger scale checks.

## Pillar 2: Volume

Metrics:

- Records per micro-batch.
- Expected vs actual message delta.
- Drop/spike detector when deviation exceeds tolerance.

Operational interpretation:

- Sudden drops may indicate ingestion interruption.
- Sudden spikes may indicate traffic event or malformed duplication.

## Pillar 3: Schema Drift

Checks:

- Required field validation.
- Type validation.
- Unexpected field detection.
- Fail-fast/DLQ routing behavior for hard contract violations.

Operational interpretation:

- Missing required fields or type mismatches route to DLQ.
- New optional fields are warning-level until contract update is approved.

## Uptime KPI Proxy

True infrastructure uptime is not implemented in this repository.

Operational proxy metrics are used instead:

- `successful_runs / expected_runs * 100`
- `healthy_intervals / observed_intervals * 100`

These are estimated operational KPIs, not platform SLA uptime guarantees.
