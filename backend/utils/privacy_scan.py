"""
privacy_scan.py
---------------
Shared detectors used by the privacy tests and the report generator to prove
that no sensitive personal data leaks into stored records or generated files.

ISO-8601 timestamps (e.g. 2026-09-29T10:15:00) are removed before scanning so
that they are not mistaken for phone numbers or birth dates.
"""

import re

ISO_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2})?)?")

PATTERNS = {
    # 10-15 digit sequences, optionally +/space/dash separated - i.e. phone-like
    "phone": re.compile(r"(?<![\w-])\+?\d(?:[ -]?\d){9,14}(?![\w-])"),
    "email": re.compile(r"[\w.\-]+@[\w\-]+\.[A-Za-z]{2,}"),
    "date_of_birth": re.compile(r"(?<![\w-])\d{1,2}[/.]\d{1,2}[/.](?:19|20)\d{2}(?![\w-])"),
    "password": re.compile(r"password\s*[:=]\s*\S+", re.I),
    "coordinates": re.compile(r"(?<![\w.])-?\d{1,3}\.\d{4,},\s*-?\d{1,3}\.\d{4,}"),
}


def strip_timestamps(text: str) -> str:
    return ISO_TIMESTAMP.sub(" ", text)


def scan(text: str) -> dict:
    """Return {pattern_name: first_match_or_None} for sensitive patterns."""
    cleaned = strip_timestamps(text)
    result = {}
    for name, rx in PATTERNS.items():
        match = rx.search(cleaned)
        result[name] = match.group() if match else None
    return result


def has_sensitive_data(text: str) -> bool:
    return any(value for value in scan(text).values())
