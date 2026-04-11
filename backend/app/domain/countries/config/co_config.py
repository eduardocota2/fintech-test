from app.domain.scoring.engine import ScoringFactor, ScoringThresholds
from app.domain.scoring.factors import (
    amount_to_income_calculator,
    credit_score_calculator,
    debt_to_income_calculator,
    document_validity_calculator,
    income_stability_calculator,
)

# Factor weights
WEIGHT_DEBT_TO_INCOME = 0.35
WEIGHT_AMOUNT_TO_INCOME = 0.25
WEIGHT_CREDIT_SCORE = 0.25
WEIGHT_INCOME_STABILITY = 0.10
WEIGHT_DOCUMENT_VALIDITY = 0.05

# Scoring configuration
MAX_ACCEPTABLE_DEBT_RATIO = 0.40
DEBT_CURVE = "strict"
MAX_AMOUNT_MULTIPLIER = 15
MAX_AMOUNT_MULTIPLIER = 8
OPTIMAL_AMOUNT_MULTIPLIER = 3.5
CREDIT_SCORE_MIN = 150
CREDIT_SCORE_MAX = 950
CREDIT_SCORE_EXCELLENT = 780
CREDIT_SCORE_POOR = 500

MIN_WAGE_MONTHLY_COP_2026 = 1750905
MIN_STABLE_INCOME = MIN_WAGE_MONTHLY_COP_2026
OPTIMAL_STABLE_INCOME = MIN_WAGE_MONTHLY_COP_2026 * 3.0

# Decision thresholds
AUTO_APPROVE_MIN = 710
MANUAL_REVIEW_MIN = 560
HARD_REJECT_MAX = 560

# Hard-rule thresholds
HARD_MAX_DEBT_RATIO = 0.55
HARD_MAX_AMOUNT_MULTIPLIER = 10
HARD_MIN_CREDIT_SCORE = 300
HARD_MIN_MONTHLY_INCOME = MIN_WAGE_MONTHLY_COP_2026 * 0.7

CO_FACTORS = [
    ScoringFactor(
        name="debt_to_income",
        weight=WEIGHT_DEBT_TO_INCOME,
        calculator=debt_to_income_calculator(
            max_acceptable=MAX_ACCEPTABLE_DEBT_RATIO,
            curve=DEBT_CURVE,
        ),
        description="Total debt versus monthly income",
    ),
    ScoringFactor(
        name="amount_to_income",
        weight=WEIGHT_AMOUNT_TO_INCOME,
        calculator=amount_to_income_calculator(
            max_multiplier=MAX_AMOUNT_MULTIPLIER,
            optimal_multiplier=OPTIMAL_AMOUNT_MULTIPLIER,
        ),
        description="Requested amount versus monthly income",
    ),
    ScoringFactor(
        name="credit_score",
        weight=WEIGHT_CREDIT_SCORE,
        calculator=credit_score_calculator(
            min_score=CREDIT_SCORE_MIN,
            max_score=CREDIT_SCORE_MAX,
            excellent_threshold=CREDIT_SCORE_EXCELLENT,
            poor_threshold=CREDIT_SCORE_POOR,
        ),
        description="Datacredito score hint",
    ),
    ScoringFactor(
        name="income_stability",
        weight=WEIGHT_INCOME_STABILITY,
        calculator=income_stability_calculator(
            min_income=MIN_STABLE_INCOME,
            optimal_income=OPTIMAL_STABLE_INCOME,
        ),
        description="Monthly income stability",
    ),
    ScoringFactor(
        name="document_validity",
        weight=WEIGHT_DOCUMENT_VALIDITY,
        calculator=document_validity_calculator("CC"),
        description="Document confidence signal",
    ),
]

CO_THRESHOLDS = ScoringThresholds(
    auto_approve_min=AUTO_APPROVE_MIN,
    manual_review_min=MANUAL_REVIEW_MIN,
    hard_reject_max=HARD_REJECT_MAX,
)


def co_hard_rules():
    return [
        lambda ctx: (
            (ctx.provider_total_debt or 0) / max(ctx.monthly_income, 1) <= HARD_MAX_DEBT_RATIO,
            "Deuda total excede ingreso mensual",
        ),
        lambda ctx: (
            ctx.amount_requested / max(ctx.monthly_income, 1) <= HARD_MAX_AMOUNT_MULTIPLIER,
            "Monto solicitado excede 10x el ingreso mensual",
        ),
        lambda ctx: (
            (ctx.provider_score_hint or 0) >= HARD_MIN_CREDIT_SCORE,
            "Score de crédito críticamente bajo",
        ),
        lambda ctx: (
            ctx.monthly_income >= HARD_MIN_MONTHLY_INCOME,
            "Ingreso mensual por debajo del mínimo legal",
        ),
    ]


CO_CONFIG = {
    "country_code": "CO",
    "factors": CO_FACTORS,
    "thresholds": CO_THRESHOLDS,
    "hard_rules": co_hard_rules,
    "currency": "COP",
    "document_type": "CC",
}
