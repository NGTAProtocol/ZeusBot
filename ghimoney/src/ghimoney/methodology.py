"""Load and validate a versioned scoring methodology (Directive §44)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from ghimoney.canonical import sha256_json

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "scoring.yaml"

Normalization = Literal["log_saturating", "log_decay", "fraction", "boolean"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DimensionConfig(Strict):
    weight: float
    core: bool


class AggregationConfig(Strict):
    min_coverage: float
    min_observable_dimensions: int
    max_missing_core_dimensions: int
    min_dimension_metric_coverage: float


class MetricConfig(Strict):
    dimension: str
    weight: float
    normalization: Normalization
    anchor: float | None = None

    @model_validator(mode="after")
    def _anchor_required(self) -> "MetricConfig":
        if self.normalization.startswith("log_") and not (self.anchor and self.anchor > 0):
            raise ValueError("log normalization requires a positive anchor")
        return self


class ConfidenceConfig(Strict):
    evidence_kind: dict[str, float]
    risk_adjustment: dict[str, float]


class IngestionConfig(Strict):
    window_days: int
    per_page: int
    max_pages_commits: int
    max_pages_contributors: int
    max_pages_releases: int
    security_policy_paths: list[str]


class Methodology(Strict):
    methodology_version: str
    config_version: str
    dimensions: dict[str, DimensionConfig]
    aggregation: AggregationConfig
    metrics: dict[str, MetricConfig]
    confidence: ConfidenceConfig
    risk: dict[str, dict[str, float | int | str]]
    ingestion: IngestionConfig

    @model_validator(mode="after")
    def _consistent(self) -> "Methodology":
        total = sum(d.weight for d in self.dimensions.values())
        if not math.isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(f"dimension weights must sum to 1.0, got {total}")
        for name, metric in self.metrics.items():
            if metric.dimension not in self.dimensions:
                raise ValueError(f"metric {name} references unknown dimension {metric.dimension}")
        for dim in self.dimensions:
            weights = [m.weight for m in self.metrics.values() if m.dimension == dim]
            if weights and not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
                raise ValueError(f"metric weights of dimension {dim} must sum to 1.0")
        return self

    @property
    def config_hash(self) -> str:
        return sha256_json(self.model_dump(mode="json"))

    def metrics_of(self, dimension: str) -> dict[str, MetricConfig]:
        return {n: m for n, m in self.metrics.items() if m.dimension == dimension}


def load_methodology(path: Path | str | None = None) -> Methodology:
    with open(path or DEFAULT_CONFIG, encoding="utf-8") as fh:
        return Methodology.model_validate(yaml.safe_load(fh))
