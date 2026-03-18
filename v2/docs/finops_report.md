# FinOps Report: v2 Kafka + Databricks Streaming Pipeline

## Purpose

This report documents cost-aware design choices and the measurement framework used to compare v1 and v2. The goal is not just theoretical pricing awareness. The goal is to connect pipeline design choices to measured batch behavior, expected cost drivers, and tradeoffs between reliability and spend.

## 1) Measured Inputs for Cost Analysis

This repository now captures benchmark-oriented micro-batch metrics that can be used as direct inputs to cost analysis.

Operational benchmark inputs:

- `run_id`
- `job_name`
- `batch_id`
- `batch_processed_ts`
- `row_count`
- `target_table`

These rows are written to `OPS_METRICS_TABLE` and make it possible to compare baseline, replay, malformed-input, and stress-test runs using measured job behavior rather than architecture claims alone.

## 2) Why Job Compute Over Interactive Clusters for Repeatable ETL

For scheduled ingestion and transformation, Databricks job compute is preferred because it is easier to bound and attribute:

- Jobs start for a workload and terminate after completion, reducing idle runtime.
- Compute policy can enforce instance families, autoscaling bounds, and runtime limits.
- Cost attribution is cleaner by job and run than shared interactive clusters.
- Operational behavior is more reproducible across benchmark scenarios.

Interactive clusters remain useful for exploration and incident debugging, but they are not the primary execution surface for repeatable ETL due to idle cost and governance drift.

## 3) Checkpoint and Storage Tradeoffs

Streaming checkpoints are non-optional for fault tolerance and progress tracking, but they introduce persistent storage cost.

Tradeoffs:

- More granular micro-batches can improve latency but can increase checkpoint churn.
- Long-lived state and frequent metadata writes can grow storage over time.
- Deleting checkpoints too aggressively can break recovery semantics.

Practical approach:

- Use dedicated checkpoint paths per job and environment.
- Monitor checkpoint growth trend, not just absolute size.
- Pair checkpoint retention strategy with replay and runbook expectations.

## 4) Delta Retention and Cost Considerations

Delta cost posture should align to layer purpose:

- Bronze keeps replayable raw history long enough for backfill and audit needs.
- Silver retains enough history for contract debugging and feature reprocessing.
- Serving tables optimize for downstream access patterns rather than raw recovery.

Cost and risk notes:

- Overly long retention inflates storage and metadata scan overhead.
- Overly short retention can break incident recovery and historical reprocessing.
- VACUUM and OPTIMIZE cadence should be explicit and environment-specific.

## 5) Expected Compute Hotspots in This Pipeline

Likely hotspots include:

- regex-heavy feature extraction in `silver_features`
- high-volume string normalization in `silver_parse`
- minute-level operational and engagement rollups downstream in dbt
- replay windows or bursty workloads that compress more work into fewer batches

Mitigation strategy:

- keep Bronze minimal
- stage canonical parsing before downstream heuristics
- reuse intermediate expressions where possible
- measure batch shape changes before and after feature additions

## 6) Cost per Million Messages Processed

A practical portfolio KPI is unit economics at message scale.

Baseline formula:

`cost_per_million_messages_usd = (total_pipeline_cost_usd / total_messages_processed) * 1000000`

Where `total_pipeline_cost_usd` should include:

- streaming job compute
- scheduled dbt or serving-model compute
- storage for Delta and checkpoints, allocated proportionally
- relevant Kafka and cloud costs included in the comparison scope

Interpretation guidance:

- compare by `run_id`
- compare baseline versus stress-test scenarios
- pair cost with DLQ rate, freshness, and throughput so cost reductions do not hide quality regressions

## 7) Native Spark Expressions vs Python UDF Cost Impact

Native Spark expressions are preferred in this pipeline for cost and performance reasons:

- Catalyst optimization is available for native expressions.
- Python serialization overhead is reduced.
- Execution plans remain easier to inspect.
- Batch comparisons stay easier to attribute when logic remains within Spark's native engine.

Python UDFs are reserved for cases without practical native equivalents. If introduced, they should be measured with before-and-after cost and latency comparisons.

## 8) Practical Cost-Control Recommendations

1. Enforce cluster policies for all scheduled jobs.
2. Use environment-specific schedules; avoid production cadence in dev.
3. Set explicit retention policies for Bronze, Silver, and checkpoint locations.
4. Review feature logic for regex or shuffle-heavy regressions.
5. Prefer incremental dbt materializations where semantics allow.
6. Tag runs consistently by pipeline, environment, owner, and benchmark scenario.
7. Track cost and reliability together using unit economics plus freshness and DLQ indicators.

## 9) What to Add Once Benchmark Numbers Are Finalized

When measured numbers are ready, expand this report with:

- runtime summary by `run_id`
- total rows processed by job
- mean and percentile batch sizes by job
- DLQ rate by scenario
- estimated cost per million messages by scenario
- v1 versus v2 comparison notes tied to specific design changes

That final section is where the report moves from cost-aware framework to measured cost comparison.
