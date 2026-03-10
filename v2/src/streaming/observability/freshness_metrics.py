from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class FreshnessSnapshot:
    event_to_ingest_lag_seconds: float
    bronze_to_silver_lag_seconds: float
    last_successful_batch_age_seconds: float


def event_time_to_ingest_lag_seconds(event_ts: datetime, ingest_ts: datetime) -> float:
    return max((ingest_ts - event_ts).total_seconds(), 0.0)


def bronze_to_silver_latency_seconds(bronze_ts: datetime, silver_ts: datetime) -> float:
    return max((silver_ts - bronze_ts).total_seconds(), 0.0)


def last_successful_batch_age_seconds(last_success_ts: datetime) -> float:
    now = datetime.now(timezone.utc)
    return max((now - last_success_ts).total_seconds(), 0.0)


def build_freshness_snapshot(event_ts: datetime, ingest_ts: datetime, silver_ts: datetime, last_success_ts: datetime) -> FreshnessSnapshot:
    return FreshnessSnapshot(
        event_to_ingest_lag_seconds=event_time_to_ingest_lag_seconds(event_ts, ingest_ts),
        bronze_to_silver_lag_seconds=bronze_to_silver_latency_seconds(ingest_ts, silver_ts),
        last_successful_batch_age_seconds=last_successful_batch_age_seconds(last_success_ts),
    )
