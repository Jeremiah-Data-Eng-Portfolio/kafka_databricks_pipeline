# Twitch Chat Streaming Pipeline Case Study

This repository contains two versions of the same Twitch chat analytics project.

- `v1/prototype`: the original end-to-end prototype
- `v2`: a refactored version with cleaner medallion boundaries, explicit DLQ handling, operational benchmark metrics, and dbt serving models

## Repository Purpose

This repo is designed as a side-by-side case study.

The `v1` prototype shows the original pipeline working end to end. The `v2` version shows how the same use case was redesigned with clearer layer ownership, a stronger streaming contract boundary, explicit dead-letter handling, batch-level operational metrics, and downstream serving models for both engagement and operational reporting.

## Repository Layout

- `v1/`  
  Preserved prototype artifacts

- `v2/`  
  Refactored pipeline code, documentation, Databricks job scaffolding, and dbt models

## v1 vs v2

### v1

The prototype version demonstrates pipeline feasibility for the Twitch chat use case.

It includes:

- original ingestion and transformation flow
- prototype dbt models and outputs
- architecture images and supporting notes

### v2

The refactored version focuses on a more defensible streaming design and measurable operational behavior.

It includes:

- append-only Bronze ingest
- Silver parsing, validation, and deduplication
- explicit DLQ routing for malformed or invalid records
- separate Silver feature derivation logic
- batch-level operational metrics using `run_id` and `batch_id`
- dbt models for engagement and operational reporting
- supporting architecture notes, ADRs, runbooks, and cost analysis documentation

## Start Here

1. Prototype path: [`v1/prototype/README.md`](v1/prototype/README.md)
2. Refactored path: [`v2/README.md`](v2/README.md)