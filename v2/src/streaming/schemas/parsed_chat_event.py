from __future__ import annotations

PARSED_CHAT_REQUIRED_FIELDS = {
    "event_id",
    "source_topic",
    "source_partition",
    "source_offset",
    "event_ts",
    "bronze_ingestion_ts",
    "silver_processed_ts",
    "channel",
    "chatter_id",
    "message_text",
}


def parsed_chat_schema_definition() -> dict:
    """Typed Silver contract for validated chat events."""

    return {
        "event_id": "string",
        "source_topic": "string",
        "source_partition": "int",
        "source_offset": "long",
        "event_ts": "timestamp",
        "bronze_ingestion_ts": "timestamp",
        "silver_processed_ts": "timestamp",
        "channel": "string",
        "chatter_id": "string",
        "message_text": "string",
        "message_text_normalized": "string",
        "message_length": "int",
        "source_platform": "string",
    }


def parsed_chat_required_fields() -> set[str]:
    return set(PARSED_CHAT_REQUIRED_FIELDS)
