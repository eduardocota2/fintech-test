from __future__ import annotations

import math
from typing import Callable

from app.domain.countries.base import CountryContext

FactorCalculator = Callable[[CountryContext], float]

SCORE_MIN = 0.0
SCORE_MAX = 1000.0
EPSILON_NON_ZERO = 1
LOW_RATIO_EXCELLENT_THRESHOLD = 3
AMOUNT_SCORE_OPTIMAL_FLOOR = 750.0
EARLY_RATIO_SEGMENT_DELTA = 250.0
LOG_LENIENT_SCALE = 10
POOR_SCORE_DEFAULT_FRACTION = 0.2


def debt_to_income_calculator(max_acceptable: float, curve: str = "linear") -> FactorCalculator:
    def calculate(context: CountryContext) -> float:
        debt = context.provider_total_debt or 0
        income = max(context.monthly_income, EPSILON_NON_ZERO)
        ratio = debt / income

        if ratio <= 0:
            return SCORE_MAX
        if ratio >= max_acceptable:
            return SCORE_MIN

        normalized = ratio / max_acceptable
        if curve == "linear":
            return SCORE_MAX * (1 - normalized)
        if curve == "strict":
            return SCORE_MAX * (1 - normalized**2)
        if curve == "lenient":
            return SCORE_MAX * (
                1 - math.log1p(normalized * LOG_LENIENT_SCALE) / math.log1p(LOG_LENIENT_SCALE)
            )
        raise ValueError(f"Unknown curve type: {curve}")

    return calculate


def amount_to_income_calculator(max_multiplier: float, optimal_multiplier: float | None = None) -> FactorCalculator:
    optimal = optimal_multiplier or (max_multiplier / 2)

    def calculate(context: CountryContext) -> float:
        ratio = context.amount_requested / max(context.monthly_income, EPSILON_NON_ZERO)

        if ratio <= optimal:
            if ratio <= LOW_RATIO_EXCELLENT_THRESHOLD:
                return SCORE_MAX
            denominator = max(optimal - LOW_RATIO_EXCELLENT_THRESHOLD, EPSILON_NON_ZERO)
            return SCORE_MAX - (
                EARLY_RATIO_SEGMENT_DELTA * (ratio - LOW_RATIO_EXCELLENT_THRESHOLD) / denominator
            )

        if ratio >= max_multiplier:
            return SCORE_MIN

        progress = (ratio - optimal) / max(max_multiplier - optimal, EPSILON_NON_ZERO)
        return AMOUNT_SCORE_OPTIMAL_FLOOR * (1 - progress)

    return calculate


def credit_score_calculator(
    *,
    min_score: int,
    max_score: int,
    excellent_threshold: int,
    poor_threshold: int | None = None,
) -> FactorCalculator:
    poor = poor_threshold or (min_score + int((max_score - min_score) * POOR_SCORE_DEFAULT_FRACTION))

    def calculate(context: CountryContext) -> float:
        score = context.provider_score_hint or min_score
        score = max(min_score, min(max_score, score))

        if score >= excellent_threshold:
            return SCORE_MAX
        if score <= poor:
            return SCORE_MIN

        return SCORE_MAX * (score - poor) / max(excellent_threshold - poor, EPSILON_NON_ZERO)

    return calculate


def income_stability_calculator(
    *,
    min_income: float,
    optimal_income: float,
    currency_factor: float = 1.0,
) -> FactorCalculator:
    def calculate(context: CountryContext) -> float:
        income = context.monthly_income * currency_factor
        if income < min_income:
            return SCORE_MIN
        if income >= optimal_income:
            return SCORE_MAX
        return SCORE_MAX * (income - min_income) / max(optimal_income - min_income, EPSILON_NON_ZERO)

    return calculate


def document_validity_calculator(document_type: str) -> FactorCalculator:
    _ = document_type

    def calculate(context: CountryContext) -> float:
        _ = context
        return SCORE_MAX

    return calculate


def composite_calculator(factors: list[tuple[FactorCalculator, float]]) -> FactorCalculator:
    def calculate(context: CountryContext) -> float:
        total_score = 0.0
        for calc, weight in factors:
            total_score += calc(context) * weight
        return total_score

    return calculate
