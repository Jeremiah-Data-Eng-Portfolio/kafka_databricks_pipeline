from __future__ import annotations

REQUIRED_RAW_FIELDS = {
    "ingestion_ts",
    "source",
    "raw",
}

RAW_EVENT_EXPECTED_SOURCE_FIELDS = {
    "platform",
    "protocol",
    "server",
    "channel",
}

RAW_EVENT_EXPECTED_RAW_FIELDS = {
    "irc_line",
    "username",
    "message",
}


def raw_event_schema_definition() -> dict:
    """Permissive contract for raw capture at Bronze boundary."""

    return {
        "ingestion_ts": "timestamp",
        "source": {
            "platform": "string",
            "protocol": "string",
            "server": "string",
            "channel": "string",
        },
        "raw": {
            "irc_line": "string",
            "username": "string",
            "message": "string",
        },
        "metadata": {
            "event_kind": "string",
            "producer_env": "string",
            "schema_version": "string",
        },
    }


def raw_event_required_fields() -> set[str]:
    return set(REQUIRED_RAW_FIELDS)
