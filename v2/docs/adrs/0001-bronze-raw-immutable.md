# ADR 0001: Keep Bronze append-only and enforce canonical deduplication in Silver

- Status: Accepted
- Date: 2026-03-08

## Context

This pipeline ingests high-volume Twitch chat events from Kafka into a Databricks / Delta Lake medallion architecture.

The core architectural question is where idempotency and duplicate protection should be enforced:

1. **Bronze-level technical idempotency**
   - Use `foreachBatch` plus Delta `MERGE` in Bronze.
   - Enforce uniqueness using Kafka source coordinates such as `(source_topic, source_partition, source_offset)`.

2. **Silver-level canonical deduplication**
   - Keep Bronze as a raw append-oriented landing layer.
   - Preserve Kafka source coordinates and raw payload in Bronze.
   - Enforce canonical uniqueness and contract validation in Silver.

Databricks medallion guidance frames Bronze as the raw ingestion layer and Silver as the layer where cleanup and validation occur.

Delta Lake’s native Structured Streaming sink supports exactly-once processing through the Delta transaction log, while `foreachBatch()` only provides at-least-once guarantees unless idempotency is implemented explicitly by the developer.

This matters because Bronze ingestion is expected to handle potentially large event volume. For append-heavy event streams, introducing `foreachBatch + MERGE` at Bronze increases:
- micro-batch compute cost
- transaction overhead
- code complexity
- operational surface area

At the same time, downstream business metrics such as chat volume, engagement, spam rate, and moderation signals still require canonical duplicate protection.

## Decision

We will keep **Bronze append-only** in v2 and preserve:
- raw payload
- Kafka source coordinates
- Kafka timestamp
- ingestion timestamp

We will enforce **canonical deduplication and contract validation in Silver**.

Silver is the first layer that will be treated as the canonical parsed event contract for downstream analytics. Duplicate handling will be based on the stable technical event identity:
- `source_topic`
- `source_partition`
- `source_offset`

Malformed or contract-breaking records will be routed to the DLQ in Silver.

## Rationale

### Why not enforce deduplication in Bronze?

Bronze is intended to remain as close to source truth as possible, with minimal transformation. That aligns with the medallion model where Bronze captures raw ingestion and Silver performs cleanup and validation.

For this pipeline, Bronze deduplication would require custom sink logic such as `foreachBatch + MERGE`. `foreachBatch()` is at-least-once by default and requires explicit idempotency reasoning by the developer. It also introduces serialization and latency tradeoffs relative to standard streaming writes.

Because this source is Kafka and already provides stable source coordinates, we can preserve those coordinates in Bronze and enforce uniqueness in Silver without paying the merge cost on every raw ingest batch.

### Why Silver?

Silver is the right place to define the canonical parsed event contract:
- parsed schema
- required fields
- normalized channel / chatter / message fields
- DLQ routing
- uniqueness enforcement

This makes Silver the trust boundary for downstream analytics. Gold models then consume a stable, validated, deduplicated event stream.

### Why is this more production-realistic?

For high-volume append-oriented event data, production teams often optimize the ingest path for:
- throughput
- operational simplicity
- replayability
- cost efficiency

They still care deeply about idempotent outcomes, but that does not require every raw landing table to execute `MERGE` logic. Delta’s native streaming sink already provides strong transactional guarantees for streaming writes, and preserving replay metadata in Bronze allows Silver to own canonical uniqueness without losing traceability.

## Consequences

### Positive
- Bronze remains simple, raw, and inexpensive relative to a merge-based sink.
- Kafka coordinates remain available for replay, traceability, and deterministic deduplication.
- Silver becomes the explicit contract boundary for data quality and canonical event identity.
- The architecture is easier to explain in medallion terms:
  - Bronze = raw capture
  - Silver = validated canonical event set
  - Gold = stakeholder metrics

### Negative
- Bronze may contain duplicate technical events in rare replay or reprocessing scenarios.
- Silver must take on the responsibility of enforcing uniqueness.
- Observability must make duplicate rates visible so that upstream issues are not hidden.

### Operational implications
- Silver must implement deterministic deduplication on Kafka source coordinates.
- DLQ handling must happen before invalid or malformed records reach canonical downstream tables.
- Runbooks must explain replay behavior and how Bronze duplicates are reconciled by Silver.

## Alternatives considered

### 1. Bronze `foreachBatch + MERGE`
Rejected as the default v2 design.

This approach is defensible and increases raw-layer duplicate protection, but for this event stream it adds compute and complexity too early in the pipeline. It is better suited to use cases where:
- Bronze itself is a consumer-facing contract
- mutable records or CDC require upsert semantics
- duplicate raw landing creates unacceptable downstream waste immediately

### 2. No canonical deduplication at all
Rejected.

Downstream business metrics would become unreliable if duplicate events were allowed to flow unchecked into Silver and Gold.

## Implementation notes

Bronze:
- append-only streaming write to Delta
- preserve raw payload and Kafka source coordinates

Silver:
- parse raw payload
- validate schema / contract
- route malformed records to DLQ
- deduplicate on `(source_topic, source_partition, source_offset)` or derived `event_id`

Gold:
- consume only canonical Silver tables

## Review trigger

Revisit this ADR if:
- Bronze becomes a direct consumer-facing dataset
- source behavior changes from append-only events to CDC / mutable state
- duplicate rates in Bronze become operationally costly enough to justify Bronze-level merge semantics
- latency or correctness requirements change materially
