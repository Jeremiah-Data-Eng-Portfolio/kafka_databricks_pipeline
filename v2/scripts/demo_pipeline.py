from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from producer.config import ProducerConfig
from producer.twitch_producer import build_event_envelope
from streaming.jobs.dlq_router import build_dlq_event
from streaming.observability.freshness_metrics import build_freshness_snapshot
from streaming.observability.pipeline_slo import pipeline_uptime_proxy_percent
from streaming.observability.volume_metrics import build_volume_snapshot
from streaming.transforms.feature_engineering import (
    emote_count,
    is_engagement_indicator,
    is_spam_indicator,
    message_length,
)
from streaming.transforms.parsing import parse_raw_event, to_parsed_contract
from streaming.transforms.quality_rules import assess_record


def demo() -> None:
    cfg = ProducerConfig(
        environment="demo",
        kafka_bootstrap_servers="localhost:9092",
        kafka_raw_topic="twitch_chat_raw",
        kafka_client_id="demo-producer",
        twitch_server="irc.chat.twitch.tv",
        twitch_port=6667,
        twitch_nick="demo_user",
        twitch_token="oauth:demo",
        twitch_channel="#demo_channel",
        poll_timeout_seconds=30,
        kafka_retries=3,
        kafka_retry_backoff_ms=500,
    )

    sample_line = ":demo_user!demo_user@demo.tmi.twitch.tv PRIVMSG #demo_channel :GG what a play!!!"

    envelope = build_event_envelope(sample_line, cfg)
    raw_payload = json.dumps(envelope)
    parsed = parse_raw_event(raw_payload)

    parsed_contract = to_parsed_contract(parsed, topic="twitch_chat_raw", partition=0, offset=1)
    quality = assess_record(parsed_contract)

    feature_summary = {
        "message_length": message_length(parsed_contract["message_text"]),
        "emote_count": emote_count(parsed_contract["message_text"]),
        "engagement_signal": is_engagement_indicator(parsed_contract["message_text"]),
        "spam_indicator": is_spam_indicator(parsed_contract["message_text"]),
    }

    freshness = build_freshness_snapshot(
        event_ts=datetime.now(timezone.utc) - timedelta(seconds=6),
        ingest_ts=datetime.now(timezone.utc) - timedelta(seconds=2),
        silver_ts=datetime.now(timezone.utc),
        last_success_ts=datetime.now(timezone.utc) - timedelta(seconds=15),
    )
    volume = build_volume_snapshot(expected=1000, actual=1085, tolerance_ratio=0.05)
    uptime_proxy = pipeline_uptime_proxy_percent(successful_runs=1420, expected_runs=1440)

    print("=== V2 Demo: Parsed Contract ===")
    print(json.dumps(parsed_contract, default=str, indent=2))

    print("\n=== V2 Demo: Quality Assessment ===")
    print(json.dumps({
        "accepted": quality.accepted,
        "dlq_issues": [issue.__dict__ for issue in quality.dlq_issues],
        "warn_issues": [issue.__dict__ for issue in quality.warn_issues],
    }, indent=2))

    print("\n=== V2 Demo: Features ===")
    print(json.dumps(feature_summary, indent=2))

    print("\n=== V2 Demo: Observability ===")
    print(json.dumps({
        "freshness": freshness.__dict__,
        "volume": volume.__dict__,
        "uptime_proxy_percent": uptime_proxy,
    }, indent=2))

    if not quality.accepted:
        dlq_event = build_dlq_event(
            raw_payload=raw_payload,
            error_reason="; ".join(issue.detail for issue in quality.dlq_issues),
            retryable=False,
            source_topic="twitch_chat_raw",
            source_partition=0,
            source_offset=1,
            error_code="CONTRACT_ERROR",
        )
        print("\n=== V2 Demo: DLQ Event ===")
        print(json.dumps(dlq_event.__dict__, default=str, indent=2))


if __name__ == "__main__":
    demo()
