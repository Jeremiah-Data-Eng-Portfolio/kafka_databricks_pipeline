# Future AI Readiness

## Why AI Is Deferred in v2

This version prioritizes streaming reliability, contract governance, and operational observability before introducing model-heavy components.

## Future Architecture Notes

- Hybrid toxicity detection: rule-based prefilter + model-based classifier.
- Emote-aware embeddings to capture channel-specific semantics.
- LLM-assisted context classification for nuanced conversation states.
- Offline feature store + batch/near-real-time model scoring path.

## Why Deferred

- Requires labeled data strategy and evaluation framework.
- Increases inference cost and latency complexity.
- Needs model governance (versioning, monitoring, rollback) not yet in scope.

## Prerequisites Already Established

- Immutable replayable Bronze history.
- DLQ corpus for failure/error analysis.
- Deterministic Silver feature baseline.
- Observability signals that can extend to model/data drift.
