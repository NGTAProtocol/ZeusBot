"""Core data models for the GHIMONEY Impact Engine."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Availability(str, Enum):
    """Why a value is (or is not) present. Missing data is never zero (Rule 3)."""

    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_MEASURABLE = "NOT_MEASURABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def rank(self) -> int:
        return ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(self.value)


class ImpactStatus(str, Enum):
    SCORED = "SCORED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Provenance(Frozen):
    source: str
    request_keys: list[str]
    endpoints: list[str]
    response_hashes: list[str]
    retrieved_at: str


class EvidenceRecord(Frozen):
    """One observed fact about a project (Directive §8, extended per audit §5)."""

    evidence_id: str
    project_id: str
    metric: str
    availability: Availability
    evidence_kind: str | None
    raw_value: Any
    normalized_value: float | None
    method: str
    confidence: float | None
    provenance: Provenance
    as_of: str
    methodology_version: str
    note: str | None = None


class DimensionResult(Frozen):
    dimension: str
    availability: Availability
    weight: float
    score: float | None
    metric_coverage: float
    confidence: float | None
    metrics_used: list[str]
    metrics_missing: list[str]


class ImpactResult(Frozen):
    status: ImpactStatus
    score: float | None
    reasons: list[str]
    original_weights: dict[str, float]
    effective_weights: dict[str, float]
    weights_renormalized: bool
    missing_dimensions: list[str]


class CoverageResult(Frozen):
    value: float
    observable_dimensions: list[str]
    missing_dimensions: list[str]


class ConfidenceResult(Frozen):
    base: float | None
    risk_adjustment_factor: float
    adjusted: float | None


class RiskSignal(Frozen):
    signal_id: str
    level: RiskLevel
    description: str
    evidence_ids: list[str]
    observed: dict[str, Any]


class RiskResult(Frozen):
    level: RiskLevel
    signals: list[RiskSignal]
    checks_evaluated: list[str]
    checks_not_evaluated: list[str] = Field(default_factory=list)


class ProjectIdentity(Frozen):
    project_id: str
    forge: str
    forge_repo_id: int
    forge_node_id: str | None
    full_name: str
    is_fork: bool | None
    is_archived: bool | None
