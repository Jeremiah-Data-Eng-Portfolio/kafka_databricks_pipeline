# ADR 0002: Parsing and Enrichment Move to Silver

## Status
Accepted

## Context
Applying parsing or enrichment too early at ingest increases coupling and makes raw recovery difficult when contracts evolve.

## Decision
Bronze remains raw; parsing, normalization, type enforcement, and reusable feature derivation are performed downstream in Silver.

## Consequences
- Establishes clean medallion boundaries and clearer ownership.
- Reduces risk of irreversible ingest-time transformation errors.
- Adds an extra processing stage that must be monitored and operated.
