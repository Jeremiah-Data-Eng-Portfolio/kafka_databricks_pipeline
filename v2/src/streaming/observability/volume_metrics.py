from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VolumeSnapshot:
    records_in_micro_batch: int
    expected_records: int
    actual_records: int
    delta_records: int
    is_spike_or_drop: bool


def records_per_micro_batch(record_count: int) -> int:
    return max(record_count, 0)


def expected_vs_actual_delta(expected: int, actual: int) -> int:
    return actual - expected


def detect_volume_spike_or_drop(expected: int, actual: int, tolerance_ratio: float = 0.25) -> bool:
    if expected <= 0:
        return False
    return abs(actual - expected) / expected > tolerance_ratio


def build_volume_snapshot(expected: int, actual: int, tolerance_ratio: float = 0.25) -> VolumeSnapshot:
    return VolumeSnapshot(
        records_in_micro_batch=records_per_micro_batch(actual),
        expected_records=expected,
        actual_records=actual,
        delta_records=expected_vs_actual_delta(expected, actual),
        is_spike_or_drop=detect_volume_spike_or_drop(expected, actual, tolerance_ratio),
    )
