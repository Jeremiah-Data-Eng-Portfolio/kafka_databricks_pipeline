# ADR 0007: Preserve v1 and Introduce v2 Instead of Destructive Refactor

## Status
Accepted

## Context
The project needed stronger production signaling without losing evidence of the original working prototype.

## Decision
Keep v1 as preserved historical implementation and build v2 as a clean production-oriented architecture track, rather than rewriting v1 destructively.

## Consequences
- Maintains a transparent evolution narrative for reviewers and hiring managers.
- Reduces risk of accidentally losing prototype behavior or artifacts.
- Requires discipline to avoid cross-version duplication and keep boundaries clean.
