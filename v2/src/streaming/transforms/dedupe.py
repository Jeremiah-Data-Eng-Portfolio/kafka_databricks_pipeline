from __future__ import annotations


def build_event_key(topic: str, partition: int, offset: int) -> str:
    """Deterministic replay-safe identity for Kafka-backed events."""

    return f"{topic}:{partition}:{offset}"


def merge_key_columns() -> tuple[str, ...]:
    return ("source_topic", "source_partition", "source_offset")


def merge_condition_sql(target_alias: str = "t", source_alias: str = "s") -> str:
    cols = merge_key_columns()
    return " AND ".join(f"{target_alias}.{col} = {source_alias}.{col}" for col in cols)
