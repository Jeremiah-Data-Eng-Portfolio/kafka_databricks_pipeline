# FinOps Report: v2 Kafka + Databricks Streaming Pipeline

## Purpose

This report documents cost-aware design choices for a production-oriented Twitch chat analytics pipeline. The goal is operational realism: predictable spend, measurable unit economics, and clear tradeoffs between reliability and cost.

## 1) Why Job Compute Over Interactive Clusters for Repeatable ETL

For scheduled ingestion and transformation, Databricks job compute is preferred because it is easier to bound and attribute:

- Jobs start for a workload and terminate after completion, reducing idle runtime.
- Compute policy can enforce instance families, autoscaling bounds, and runtime limits.
- Cost attribution is cleaner by job/run tags than shared interactive clusters.
- Operational behavior is more reproducible across environments (dev/stage/prod).

Interactive clusters remain useful for exploration and incident debugging, but they are not the primary execution surface for repeatable ETL due to idle-cost and governance drift.

## 2) Checkpoint and Storage Tradeoffs

Streaming checkpoints are non-optional for fault tolerance and progress tracking, but they introduce persistent storage cost.

Tradeoffs:

- More granular micro-batches can improve latency but can increase checkpoint churn.
- Long-lived state and frequent metadata writes can grow storage over time.
- Deleting checkpoints too aggressively can break recovery semantics.

Practical approach:

- Use dedicated checkpoint paths per job and environment.
- Monitor checkpoint growth trend, not just absolute size.
- Pair checkpoint retention strategy with replay/runbook expectations.

## 3) Delta Retention and Cost Considerations

Delta cost posture should align to layer purpose:

- Bronze: keep replayable raw history long enough for backfill/audit requirements.
- Silver: retain enough history for contract debugging and feature reprocessing.
- Gold: optimize for serving, with retention aligned to stakeholder access patterns.

Cost/risk notes:

- Overly long retention inflates storage and metadata scan overhead.
- Overly short retention can break incident recovery and historical reprocessing.
- VACUUM/OPTIMIZE cadence should be explicit and environment-specific.

## 4) Expected Compute Hotspots in Streaming Feature Derivation

Likely hotspots in this pipeline:

- Regex-heavy text feature extraction at Silver (spam/link/emote signals).
- Per-message string normalization on high-throughput bursts.
- High-cardinality group-bys or minute-level aggregates in downstream serving models.
- Repeated parsing logic when contract checks and feature logic are not staged cleanly.

Mitigation strategy:

- Keep Bronze minimal and push deterministic transforms to Silver in one pass.
- Reuse intermediate columns to avoid recomputing expensive expressions.
- Prefer narrow transformations before wide shuffles.
- Profile skew around high-volume stream intervals.

## 5) Cost per Million Messages Processed

A practical portfolio KPI is unit economics at message scale.

Baseline formula:

`cost_per_million_messages_usd = (total_pipeline_cost_usd / total_messages_processed) * 1_000_000`

Where `total_pipeline_cost_usd` should include:

- streaming job compute
- scheduled dbt/model compute
- storage for Delta + checkpoints (allocated proportionally)

Interpretation guidance:

- Compare by environment (dev vs prod) and by release window.
- Track trend after major logic changes (for example, added regex features).
- Pair with reliability metrics so cost cuts do not hide quality regressions.

## 6) Native Spark Expressions vs Python UDF Cost Impact

Native Spark expressions are preferred in this pipeline for cost and performance reasons:

- Catalyst optimization is available for native SQL/functions.
- Reduced Python serialization overhead and JVM/Python boundary traffic.
- Better predicate pushdown and execution plan transparency.

Python UDFs are reserved for cases without practical native equivalents. If introduced, they should be measured with before/after cost and latency deltas.

## 7) Practical Cost-Control Recommendations

1. Enforce cluster policies for all scheduled jobs (instance family, autoscaling min/max, runtime caps).
2. Use environment-specific schedules; avoid production cadence in dev.
3. Set explicit retention policies for Bronze/Silver and checkpoint locations.
4. Review feature logic quarterly for regex or shuffle-heavy regressions.
5. Prefer incremental materializations for large Gold tables where semantics allow.
6. Tag runs consistently (pipeline, environment, owner, cost-center) for attribution.
7. Track two KPI pairs together: cost-per-million and freshness/SLO compliance.

## 8) FinOps Operating Cadence (Suggested)

- Weekly: review spend anomalies, DLQ spikes, and throughput changes.
- Monthly: review unit economics trend and top compute contributors.
- Release-level: require cost-impact note for any new feature derivation or model refresh policy change.

This cadence keeps FinOps tied to engineering decisions instead of post-hoc billing review.
