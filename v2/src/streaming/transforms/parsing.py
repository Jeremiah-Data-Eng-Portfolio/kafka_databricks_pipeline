from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class ParsingError(ValueError):
    pass


def parse_raw_event(raw_payload: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ParsingError(f"invalid_json: {exc.msg}") from exc

    if not isinstance(parsed, dict):
        raise ParsingError("payload_not_object")

    return parsed


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def parse_iso_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    as_str = str(value).strip()
    if not as_str:
        return None
    try:
        return datetime.fromisoformat(as_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def to_parsed_contract(record: dict[str, Any], topic: str, partition: int, offset: int) -> dict[str, Any]:
    source = record.get("source") or {}
    raw = record.get("raw") or {}

    message_text = normalize_text(raw.get("message"))
    chatter_id = normalize_text(raw.get("username"))

    return {
        "event_id": f"{topic}:{partition}:{offset}",
        "source_topic": topic,
        "source_partition": partition,
        "source_offset": offset,
        "event_ts": parse_iso_ts(record.get("ingestion_ts")),
        "bronze_ingestion_ts": parse_iso_ts(record.get("ingestion_ts")),
        "silver_processed_ts": datetime.now(timezone.utc),
        "channel": normalize_text(source.get("channel")),
        "source_platform": normalize_text(source.get("platform")) or "twitch",
        "chatter_id": chatter_id.lower(),
        "message_text": message_text,
        "message_text_normalized": message_text.lower(),
        "message_length": len(message_text),
    }
