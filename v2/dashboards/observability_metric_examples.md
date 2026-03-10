# Observability Metric Examples

- `stream_event_time_to_ingest_lag_seconds{layer="bronze"}`
- `stream_bronze_to_silver_latency_seconds{layer="silver"}`
- `stream_records_per_micro_batch{topic="twitch_chat_raw"}`
- `stream_expected_vs_actual_delta{topic="twitch_chat_raw"}`
- `stream_dlq_records_total{failure_code="json_parse_error"}`
- `stream_schema_drift_events_total{source="twitch_chat"}`
- `pipeline_uptime_proxy_percent{env="prod"}`
