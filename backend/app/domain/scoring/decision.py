from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domain.scoring.engine import Decision


@dataclass(frozen=True)
class RiskDecisionSummary:
    decision: Decision
    score: float
    reason: str | None
    thresholds: dict[str, float]
    factors: dict[str, dict[str, Any]]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RiskDecisionSummary":
        decision_value = str(payload.get("decision", Decision.MANUAL_REVIEW.value))
        return cls(
            decision=Decision(decision_value),
            score=float(payload.get("score", 0)),
            reason=payload.get("reason") if isinstance(payload.get("reason"), str) else None,
            thresholds=payload.get("thresholds") if isinstance(payload.get("thresholds"), dict) else {},
            factors=payload.get("factors") if isinstance(payload.get("factors"), dict) else {},
        )
