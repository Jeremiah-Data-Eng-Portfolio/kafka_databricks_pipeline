from __future__ import annotations

import math
import re
from collections import Counter

_EMOTE_TOKEN = re.compile(r"^[A-Za-z0-9_]{2,24}$")
_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_REPEAT_PATTERN = re.compile(r"(.)\1{3,}")


def message_length(message: str) -> int:
    return len((message or "").strip())


def tokenize(message: str) -> list[str]:
    return [token for token in (message or "").strip().split(" ") if token]


def emote_count(message: str) -> int:
    tokens = tokenize(message)
    return sum(1 for token in tokens if _EMOTE_TOKEN.match(token) and any(c.isupper() for c in token))


def is_emote_only(message: str) -> bool:
    tokens = tokenize(message)
    if not tokens:
        return False
    return all(_EMOTE_TOKEN.match(token) for token in tokens)


def repeat_char_ratio(message: str) -> float:
    cleaned = (message or "").strip()
    if not cleaned:
        return 0.0

    counts = Counter(cleaned)
    repeated = sum(count for count in counts.values() if count > 2)
    return round(repeated / len(cleaned), 4)


def entropy_proxy(message: str) -> float:
    cleaned = (message or "").strip()
    if not cleaned:
        return 0.0
    unique_chars = len(set(cleaned))
    # Proxy chosen for fast, deterministic scoring outside Spark runtime.
    return round(math.log2(max(unique_chars, 1)), 4)


def contains_link(message: str) -> bool:
    return bool(_URL_PATTERN.search(message or ""))


def is_spam_indicator(message: str, repeat_ratio_threshold: float = 0.35) -> bool:
    text = message or ""
    return _REPEAT_PATTERN.search(text) is not None or repeat_char_ratio(text) >= repeat_ratio_threshold


def is_engagement_indicator(message: str) -> bool:
    msg_len = message_length(message)
    entropy = entropy_proxy(message)
    repeat_ratio = repeat_char_ratio(message)
    return msg_len >= 2 and entropy >= 1.0 and repeat_ratio < 0.7
