"""Metric normalization to a 0-100 scale (decision D-01: logarithmic, declared anchors)."""

from __future__ import annotations

import math
from typing import Any

from ghimoney.methodology import MetricConfig


def normalize(value: Any, cfg: MetricConfig) -> float:
    kind = cfg.normalization
    if kind == "boolean":
        if not isinstance(value, bool):
            raise TypeError(f"boolean normalization expects bool, got {value!r}")
        return 100.0 if value else 0.0
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{kind} normalization expects a number, got {value!r}")
    if value < 0:
        raise ValueError(f"{kind} normalization expects a non-negative value, got {value!r}")
    if kind == "fraction":
        if value > 1:
            raise ValueError(f"fraction normalization expects a value in [0, 1], got {value!r}")
        return 100.0 * value
    ratio = math.log1p(value) / math.log1p(cfg.anchor)
    if kind == "log_saturating":
        return 100.0 * min(1.0, ratio)
    if kind == "log_decay":
        return 100.0 * max(0.0, 1.0 - ratio)
    raise ValueError(f"unknown normalization {kind!r}")
