from __future__ import annotations


def slo_breached(error_rate: float, threshold: float = 0.01) -> bool:
    return error_rate > threshold


def successful_micro_batch_ratio(successful_batches: int, attempted_batches: int) -> float:
    if attempted_batches <= 0:
        return 0.0
    return round(successful_batches / attempted_batches, 4)


def healthy_run_percentage(healthy_runs: int, total_runs: int) -> float:
    if total_runs <= 0:
        return 0.0
    return round((healthy_runs / total_runs) * 100.0, 2)


def pipeline_uptime_proxy_percent(successful_runs: int, expected_runs: int) -> float:
    """Operational estimate, not infrastructure-level uptime."""

    if expected_runs <= 0:
        return 0.0
    return round((successful_runs / expected_runs) * 100.0, 2)


def healthy_interval_ratio_percent(healthy_intervals: int, observed_intervals: int) -> float:
    if observed_intervals <= 0:
        return 0.0
    return round((healthy_intervals / observed_intervals) * 100.0, 2)
