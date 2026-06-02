from __future__ import annotations

import re


UNSAFE_TERMS = {
    "gore",
    "kill child",
    "explicit sexual",
    "sexual minor",
}


class SafetyError(ValueError):
    """Raised when a request fails safety validation."""


def reject_unsafe_theme(theme: str) -> None:
    lowered = theme.lower()
    for term in UNSAFE_TERMS:
        if term in lowered:
            raise SafetyError(f"Unsafe theme input detected: {term}")


def sanitize_guidance(text: str, label: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    sanitized = text
    for term in sorted(UNSAFE_TERMS, key=len, reverse=True):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if pattern.search(sanitized):
            sanitized = pattern.sub("[removed unsafe content]", sanitized)
            warnings.append(f"{label} rewritten to remove unsafe content: {term}")
    sanitized = " ".join(sanitized.split())
    if not sanitized:
        raise SafetyError(f"{label} became empty after safety rewrite")
    return sanitized, warnings


def rewrite_for_consistency(text: str, required_fragments: list[str], label: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    final_text = text.strip()
    missing = [fragment for fragment in required_fragments if fragment and fragment.lower() not in final_text.lower()]
    if missing:
        final_text = f"{final_text} {' '.join(missing)}".strip()
        warnings.append(f"{label} extended with shared consistency guidance")
    return final_text, warnings

