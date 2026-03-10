# Runbook

## Incident: DLQ Spike

1. Inspect top failure code and error reason.
2. Check source topic/partition concentration for hotspot partitions.
3. Validate parser/schema release changes.
4. Classify failures by retryable vs non-retryable.
5. Backfill affected interval after fix.

## Incident: Freshness Breach

1. Check Kafka lag and consumer health.
2. Verify Spark job checkpoint progress.
3. Scale compute within FinOps limits.
4. Confirm recovery and close incident.

## Incident: Volume Drop/Spike

1. Compare expected vs actual micro-batch counts.
2. Validate producer connectivity and broker health.
3. Confirm no duplicate replay loop is active.

## Uptime KPI Proxy Procedure

Use estimated operational KPI proxies when true infrastructure uptime is unavailable:

- `uptime_proxy_percent = successful_runs / expected_runs * 100`
- `healthy_interval_percent = healthy_intervals / observed_intervals * 100`

Document these as operational estimates, not SLA-grade infrastructure uptime.
