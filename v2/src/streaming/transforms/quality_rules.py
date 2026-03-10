from __future__ import annotations

from dataclasses import dataclass
from typing import Any

REQUIRED_FIELDS = ("channel", "chatter_id", "message_text")

DLQ_SEVERITY = "DLQ"
WARN_SEVERITY = "WARN"


@dataclass(frozen=True)
class QualityIssue:
    code: str
    severity: str
    detail: str


@dataclass(frozen=True)
class QualityAssessment:
    accepted: bool
    dlq_issues: tuple[QualityIssue, ...]
    warn_issues: tuple[QualityIssue, ...]


def required_fields_present(record: dict) -> tuple[bool, tuple[str, ...]]:
    if "message_text" in record or "chatter_id" in record or "channel" in record:
        required = ("channel", "chatter_id", "message_text")
    else:
        required = ("user", "message")

    missing = tuple(field for field in required if not record.get(field))
    return (not missing, missing)


def message_within_reasonable_size(message: str, max_chars: int = 500) -> bool:
    cleaned = (message or "").strip()
    return 0 < len(cleaned) <= max_chars


def type_sanity_issues(record: dict[str, Any]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []

    if "message_length" in record and not isinstance(record.get("message_length"), int):
        issues.append(QualityIssue("message_length_type_invalid", DLQ_SEVERITY, "message_length must be int"))

    if "source_partition" in record and not isinstance(record.get("source_partition"), int):
        issues.append(QualityIssue("source_partition_type_invalid", DLQ_SEVERITY, "source_partition must be int"))

    if "source_offset" in record and not isinstance(record.get("source_offset"), int):
        issues.append(QualityIssue("source_offset_type_invalid", DLQ_SEVERITY, "source_offset must be long/int"))

    return issues


def required_field_issues(record: dict[str, Any]) -> list[QualityIssue]:
    ok, missing = required_fields_present(record)
    if ok:
        return []
    return [QualityIssue(f"missing_{field}", DLQ_SEVERITY, f"Required field {field} is missing") for field in missing]


def range_and_suspicious_issues(record: dict[str, Any]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    message = str(record.get("message_text", ""))

    if not message_within_reasonable_size(message):
        issues.append(QualityIssue("message_size_out_of_range", DLQ_SEVERITY, "Message is empty or too long"))

    if any(ord(ch) < 9 for ch in message):
        issues.append(QualityIssue("message_has_control_chars", WARN_SEVERITY, "Control characters detected"))

    return issues


def assess_record(record: dict[str, Any]) -> QualityAssessment:
    issues = required_field_issues(record) + type_sanity_issues(record) + range_and_suspicious_issues(record)
    dlq_issues = tuple(issue for issue in issues if issue.severity == DLQ_SEVERITY)
    warn_issues = tuple(issue for issue in issues if issue.severity == WARN_SEVERITY)
    return QualityAssessment(accepted=not dlq_issues, dlq_issues=dlq_issues, warn_issues=warn_issues)
