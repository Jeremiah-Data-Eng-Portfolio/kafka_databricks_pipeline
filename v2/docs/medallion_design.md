# Medallion Design

## Bronze

- Raw immutable ingest from Kafka.
- Identity key: `topic + partition + offset`.
- Append-first design supports replay and auditability.

## Silver

- Parsing of raw payload.
- Normalization of field names and basic canonical formats.
- Type enforcement and required-field validation.
- Feature derivation (engagement/spam/emote primitives).
- Contract violations route to DLQ.

## DLQ

DLQ captures records that fail parsing or contract validation with:

- raw payload
- error reason/error code
- ingestion timestamp
- source topic/partition/offset if available
- retryable flag

## Gold

- Stakeholder-facing metrics in dbt marts.
- Stable interfaces for creator operations and moderation analytics.
