from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from app.domain.countries.base import CountryContext


class Decision(str, Enum):
    APPROVED_AUTO = "approved_auto"
    MANUAL_REVIEW = "manual_review"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ScoringFactor:
    name: str
    weight: float
    calculator: Callable[[CountryContext], float]
    description: str

    def __post_init__(self) -> None:
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")


@dataclass(frozen=True)
class ScoringThresholds:
    auto_approve_min: float
    manual_review_min: float
    hard_reject_max: float | None = None

    def __post_init__(self) -> None:
        if not (0 <= self.manual_review_min <= self.auto_approve_min <= 1000):
            raise ValueError(
                "Thresholds must satisfy: 0 <= manual_review_min <= auto_approve_min <= 1000"
            )


@dataclass
class ScoringResult:
    decision: Decision
    score: float
    factors: dict[str, dict[str, Any]]
    thresholds: dict[str, float]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "score": round(self.score, 2),
            "factors": self.factors,
            "thresholds": self.thresholds,
            "reason": self.reason,
        }


HardRule = Callable[[CountryContext], tuple[bool, str | None]]


class ScoringEngine:
    def __init__(
        self,
        *,
        factors: list[ScoringFactor],
        thresholds: ScoringThresholds,
        hard_rules: list[HardRule] | None = None,
    ) -> None:
        self.factors = factors
        self.thresholds = thresholds
        self.hard_rules = hard_rules or []

        total_weight = sum(f.weight for f in factors)
        if not 0.99 <= total_weight <= 1.01:
            raise ValueError(f"Factor weights must sum to 1.0, got {total_weight}")

    def evaluate(self, context: CountryContext) -> ScoringResult:
        for rule in self.hard_rules:
            is_valid, reason = rule(context)
            if not is_valid:
                return ScoringResult(
                    decision=Decision.REJECTED,
                    score=0.0,
                    factors={},
                    thresholds={
                        "auto_approve": self.thresholds.auto_approve_min,
                        "manual_review": self.thresholds.manual_review_min,
                    },
                    reason=reason or "Hard rule validation failed",
                )

        factor_scores: dict[str, dict[str, Any]] = {}
        total_score = 0.0

        for factor in self.factors:
            try:
                raw_score = factor.calculator(context)
                raw_score = max(0.0, min(1000.0, raw_score))
            except Exception:
                raw_score = 0.0

            weighted_score = raw_score * factor.weight
            total_score += weighted_score

            factor_scores[factor.name] = {
                "weight": factor.weight,
                "raw_score": round(raw_score, 2),
                "weighted_score": round(weighted_score, 2),
                "description": factor.description,
            }

        if total_score >= self.thresholds.auto_approve_min:
            decision = Decision.APPROVED_AUTO
            reason = f"Score {total_score:.0f} exceeds auto-approval threshold"
        elif total_score >= self.thresholds.manual_review_min:
            decision = Decision.MANUAL_REVIEW
            low_factors = [
                name for name, data in factor_scores.items() if float(data["raw_score"]) < 600
            ]
            reason = f"Score {total_score:.0f} requires manual review"
            if low_factors:
                reason += f". Low factors: {', '.join(low_factors)}"
        else:
            decision = Decision.REJECTED
            reason = f"Score {total_score:.0f} below minimum threshold"

        return ScoringResult(
            decision=decision,
            score=round(total_score, 2),
            factors=factor_scores,
            thresholds={
                "auto_approve": self.thresholds.auto_approve_min,
                "manual_review": self.thresholds.manual_review_min,
            },
            reason=reason,
        )

    def explain(self, context: CountryContext) -> dict[str, Any]:
        result = self.evaluate(context)

        breakdown = [
            {
                "name": name,
                "description": data["description"],
                "weight": f"{float(data['weight']):.0%}",
                "raw_score": data["raw_score"],
                "contribution": round(float(data["weighted_score"]), 1),
            }
            for name, data in result.factors.items()
        ]
        breakdown.sort(key=lambda item: item["contribution"], reverse=True)

        return {
            "decision": result.decision.value,
            "total_score": result.score,
            "thresholds": result.thresholds,
            "reason": result.reason,
            "factor_breakdown": breakdown,
        }
