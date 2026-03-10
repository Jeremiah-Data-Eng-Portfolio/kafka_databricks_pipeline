from streaming.jobs.dlq_router import build_dlq_event


def test_build_dlq_event_contains_required_fields() -> None:
    event = build_dlq_event(
        raw_payload='{"bad": "payload"}',
        error_reason="json_parse_error",
        retryable=False,
        source_topic="twitch_chat_raw",
        source_partition=2,
        source_offset=123,
        error_code="PARSE_001",
    )

    assert event.raw_payload
    assert event.error_reason == "json_parse_error"
    assert event.retryable is False
    assert event.source_topic == "twitch_chat_raw"
    assert event.source_partition == 2
    assert event.source_offset == 123
