# ADR 0006: Prefer Native Spark Transformations Over Python UDFs

## Status
Accepted

## Context
Python UDF-heavy pipelines can reduce Spark optimizer effectiveness and increase serialization overhead in high-volume streaming workloads.

## Decision
Use native Spark SQL/functions for parsing and feature logic where possible; reserve Python UDFs for narrow cases with no practical native alternative.

## Consequences
- Better performance portability and easier optimization in Databricks/Spark environments.
- More transparent execution plans for troubleshooting.
- Some advanced logic may require more verbose native-expression implementations.
