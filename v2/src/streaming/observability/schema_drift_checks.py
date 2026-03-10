from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SchemaDriftResult:
    missing_required_fields: set[str]
    unexpected_fields: set[str]
    type_drift_fields: set[str]
    action: str


def required_fields_missing(record: dict, required_fields: set[str]) -> set[str]:
    return {field for field in required_fields if field not in record or record[field] is None}


def unexpected_fields(observed_fields: set[str], expected_fields: set[str]) -> set[str]:
    return observed_fields - expected_fields


def type_validation_errors(record: dict[str, Any], type_map: dict[str, type]) -> set[str]:
    errors: set[str] = set()
    for field, expected_type in type_map.items():
        if field in record and record[field] is not None and not isinstance(record[field], expected_type):
            errors.add(field)
    return errors


def decide_action(missing: set[str], type_errors: set[str], new_fields: set[str], fail_fast: bool = True) -> str:
    if missing or type_errors:
        return "FAIL_FAST" if fail_fast else "DLQ"
    if new_fields:
        return "WARN_AND_CONTINUE"
    return "ACCEPT"


def evaluate_schema_drift(
    record: dict[str, Any],
    required: set[str],
    expected: set[str],
    type_map: dict[str, type],
    fail_fast: bool = True,
) -> SchemaDriftResult:
    missing = required_fields_missing(record, required)
    new_fields = unexpected_fields(set(record.keys()), expected)
    type_errors = type_validation_errors(record, type_map)
    action = decide_action(missing, type_errors, new_fields, fail_fast=fail_fast)
    return SchemaDriftResult(
        missing_required_fields=missing,
        unexpected_fields=new_fields,
        type_drift_fields=type_errors,
        action=action,
    )
