# Runbook

## Primary Operational Tables

Use these tables first during triage:

- `silver.chat_dlq` for parse and contract failures
- `ops.streaming_batch_metrics` for per-job micro-batch benchmark rows
- `silver.silver_chat_parsed` for canonical validated output
- `silver.silver_chat_features` for downstream feature output

Useful identifiers:

- `run_id` groups a benchmark, stress test, or replay window
- `batch_id` identifies a specific micro-batch within a job run
- `job_name` distinguishes `bronze_ingest`, `silver_parse`, `silver_features`, and DLQ routing writes

## Incident: DLQ Spike

1. Filter `chat_dlq` to the affected `run_id` and time window.
2. Group failures by `error_category` and `error_code`.
3. Check whether the spike is concentrated in `PARSE_ERROR` or `CONTRACT_ERROR`.
4. Inspect `source_topic`, `source_partition`, and `source_offset` concentration to detect hotspot partitions or replay loops.
5. Compare DLQ micro-batches with `ops.streaming_batch_metrics` for the same `run_id` and `batch_id` range.
6. Validate whether a producer envelope change, parser change, or required-field assumption caused the spike.
7. If the issue is fixed and replay is appropriate, rerun from Bronze using the documented replay path.

Operational interpretation:

- `PARSE_ERROR` spikes usually indicate malformed payloads or parser/schema drift.
- `CONTRACT_ERROR` spikes usually indicate required fields became blank, missing, or invalid after parsing.
- DLQ volume itself is a signal and should not be deduplicated away during triage.

## Incident: Freshness Breach

1. Check the most recent `batch_processed_ts` in `ops.streaming_batch_metrics` by `job_name`.
2. Confirm whether the freshness breach starts in `bronze_ingest`, `silver_parse`, or `silver_features`.
3. Verify the affected job checkpoint path and last successful progress.
4. Review Kafka lag and producer health if Bronze has stopped advancing.
5. Review whether downstream jobs are waiting on upstream tables rather than actively processing.
6. Scale or rerun compute if recovery is required and within the benchmark/cost plan.
7. Confirm that fresh rows resume in the downstream table before closing the incident.

Operational interpretation:

- If Bronze is fresh and Silver is stale, the bottleneck is downstream of Kafka capture.
- If all jobs are stale, start with producer connectivity, broker access, and checkpoint health.
- Freshness should be evaluated with both batch metrics and table timestamps, not either one alone.

## Incident: Volume Drop or Volume Spike

1. Compare `row_count` by `job_name` in `ops.streaming_batch_metrics` for the affected `run_id`.
2. Determine whether the anomaly begins in Bronze or appears only after Silver parsing.
3. For drops, inspect DLQ volume to see whether records were diverted rather than lost.
4. For spikes, check whether the increase is a real traffic event, replay window, or malformed duplication pattern.
5. Review batch shape over time rather than only total counts; one bursty run can hide many small unstable batches.
6. Compare with the producer and broker health context before escalating.

Operational interpretation:

- Bronze spike with stable Silver may indicate filtering or contract rejection downstream.
- Bronze drop with normal Silver often means you are observing different windows or replay artifacts.
- Sustained spikes should be reviewed alongside batch duration and checkpoint growth.

## Incident: Replay or Backfill Request

1. Define the replay scope using source time range and affected jobs.
2. Confirm that Bronze retains the required raw history for the interval.
3. Confirm checkpoint strategy before rerunning jobs.
4. Use a distinct `run_id` for the replay so replay metrics do not mix with baseline runs.
5. Monitor `ops.streaming_batch_metrics` and DLQ tables during replay.
6. Validate the downstream dbt models after replay completes.

## Benchmark Review Procedure

Use this when comparing baseline, stress-test, or malformed-input runs.

1. Select the `run_id` values being compared.
2. Compare `row_count` distributions by `job_name` and `batch_id`.
3. Compare DLQ rate for each run.
4. Review whether volume shape changes unevenly across Bronze, Silver parse, and Silver features.
5. Use the benchmark summary as the measured input to the cost analysis.

## Uptime Proxy Guidance

True infrastructure uptime is not implemented in this repository.

Use proxy metrics only as operational estimates:

- `successful_runs / expected_runs * 100`
- `healthy_intervals / observed_intervals * 100`

Treat these as repository-level health indicators, not SLA-grade infrastructure uptime claims.
