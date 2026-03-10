# ADR 0003: Introduce a Dead-Letter Queue for Failed Records

## Status
Accepted

## Context
Malformed payloads and contract violations are expected in real streaming systems; silent drops or hard pipeline failure reduce reliability and observability.

## Decision
Records that fail parse/schema/quality checks are routed to a DLQ sink containing raw payload, failure metadata, ingestion timestamp, source offsets, and retryability indicator.

## Consequences
- Preserves failed records for triage, replay, and remediation workflows.
- Prevents single bad records from stopping entire streams.
- Requires DLQ monitoring, ownership, and backlog management processes.
