# Databricks YAML Notes

This folder contains a YAML scaffold for running v2 streaming tasks from a Git repo.

## Key points

- Task scripts are under `v2/scripts/` and call `run()` entrypoints.
- Libraries reference `v2/requirements.txt`.
- Environment variables in your job should match keys in `v2/.env.example`.
- Use Databricks secret scopes for sensitive values (`TWITCH_TOKEN`, etc.).

## Typical env vars to configure in job/task settings

- `APP_ENV`
- `KAFKA_BOOTSTRAP_SERVERS`
- `KAFKA_RAW_TOPIC`
- `KAFKA_SECURITY_PROTOCOL` (`SASL_SSL` for Confluent Cloud)
- `KAFKA_SASL_MECHANISM` (`PLAIN` for Confluent Cloud)
- `API_KEY` (Confluent Cloud API key)
- `API_SECRET` (Confluent Cloud API secret)
- `BRONZE_TABLE`
- `SILVER_PARSED_TABLE`
- `SILVER_FEATURES_TABLE`
- `DLQ_TABLE`
- `BRONZE_CHECKPOINT`
- `SILVER_PARSE_CHECKPOINT`
- `SILVER_FEATURES_CHECKPOINT`
- `SILVER_DEDUPE_WATERMARK`
- `ENFORCE_FAIL_FAST`
