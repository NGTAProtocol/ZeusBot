"""Canonical serialization, so equal inputs always produce equal bytes and hashes."""

from __future__ import annotations

import hashlib
import json
from typing import Any

FLOAT_DIGITS = 4


def _round(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, FLOAT_DIGITS)
    if isinstance(value, dict):
        return {k: _round(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_round(v) for v in value]
    return value


def canonical_json(value: Any, indent: int | None = None) -> str:
    return json.dumps(
        _round(value),
        sort_keys=True,
        ensure_ascii=False,
        indent=indent,
        separators=(",", ": ") if indent else (",", ":"),
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))
