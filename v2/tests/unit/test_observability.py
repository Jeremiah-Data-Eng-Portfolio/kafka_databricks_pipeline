from datetime import datetime, timedelta, timezone

from streaming.observability.freshness_metrics import (
    bronze_to_silver_latency_seconds,
    event_time_to_ingest_lag_seconds,
    last_successful_batch_age_seconds,
)
from streaming.observability.pipeline_slo import (
    pipeline_uptime_proxy_percent,
    slo_breached,
)


def test_event_time_to_ingest_lag_seconds_non_negative() -> None:
    event_ts = datetime.now(timezone.utc) - timedelta(seconds=12)
    ingest_ts = datetime.now(timezone.utc)
    assert event_time_to_ingest_lag_seconds(event_ts, ingest_ts) >= 0


def test_bronze_to_silver_latency_seconds_non_negative() -> None:
    bronze_ts = datetime.now(timezone.utc) - timedelta(seconds=8)
    silver_ts = datetime.now(timezone.utc)
    assert bronze_to_silver_latency_seconds(bronze_ts, silver_ts) >= 0


def test_last_successful_batch_age_seconds_non_negative() -> None:
    last_success = datetime.now(timezone.utc) - timedelta(seconds=30)
    assert last_successful_batch_age_seconds(last_success) >= 30


def test_slo_breached_true_when_above_threshold() -> None:
    assert slo_breached(0.02, threshold=0.01) is True


def test_pipeline_uptime_proxy_percent() -> None:
    assert pipeline_uptime_proxy_percent(95, 100) == 95.0
