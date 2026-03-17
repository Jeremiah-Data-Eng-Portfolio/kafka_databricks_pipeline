from __future__ import annotations

REQUIRED_RAW_FIELDS = {
    "ingestion_ts",
    "source",
    "raw",
}

# Kafka transport metadata is not emitted by the producer payload itself.
# These fields are appended by Spark Kafka ingestion in bronze_ingest.py.
RAW_EVENT_TRANSPORT_FIELDS = {
    "source_topic",
    "source_partition",
    "source_offset",
    "kafka_timestamp",
    "kafka_timestamp_type",
    "raw_key",
    "raw_payload",
    "bronze_ingestion_ts",
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
    """Producer envelope contract carried inside `raw_payload`.

    This describes the JSON payload emitted by `twitch_producer.py`.
    Kafka coordinates (`topic/partition/offset`) are transport metadata added
    by Bronze ingestion, not fields inside this payload object.
    """

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


def raw_event_transport_fields() -> set[str]:
    return set(RAW_EVENT_TRANSPORT_FIELDS)
