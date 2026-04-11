from app.domain.scoring.engine import ScoringFactor, ScoringThresholds
from app.domain.scoring.factors import (
    amount_to_income_calculator,
    credit_score_calculator,
    debt_to_income_calculator,
    document_validity_calculator,
    income_stability_calculator,
)

# Factor weights
WEIGHT_DEBT_TO_INCOME = 0.30
WEIGHT_AMOUNT_TO_INCOME = 0.25
WEIGHT_CREDIT_SCORE = 0.25
WEIGHT_INCOME_STABILITY = 0.15
WEIGHT_DOCUMENT_VALIDITY = 0.05

# Scoring configuration
MAX_ACCEPTABLE_DEBT_RATIO = 0.45
DEBT_CURVE = "linear"

MAX_AMOUNT_MULTIPLIER = 10
OPTIMAL_AMOUNT_MULTIPLIER = 4

CREDIT_SCORE_MIN = 400
CREDIT_SCORE_MAX = 850
CREDIT_SCORE_EXCELLENT = 740
CREDIT_SCORE_POOR = 550

MIN_WAGE_DAILY_MXN_2026 = 315.04
MIN_WAGE_MONTHLY_MXN_2026 = MIN_WAGE_DAILY_MXN_2026 * 30
MIN_STABLE_INCOME = MIN_WAGE_MONTHLY_MXN_2026
OPTIMAL_STABLE_INCOME = MIN_WAGE_MONTHLY_MXN_2026 * 3.0

# Decision thresholds
AUTO_APPROVE_MIN = 720
MANUAL_REVIEW_MIN = 560
HARD_REJECT_MAX = 560

# Hard-rule thresholds
HARD_MAX_DEBT_RATIO = 3.0
HARD_MAX_AMOUNT_MULTIPLIER = 12
HARD_MIN_CREDIT_SCORE = 500
HARD_MIN_MONTHLY_INCOME = MIN_WAGE_MONTHLY_MXN_2026 * 0.8

MX_FACTORS = [
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
        description="Bureau credit score hint",
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
        calculator=document_validity_calculator("CURP"),
        description="Document confidence signal",
    ),
]

MX_THRESHOLDS = ScoringThresholds(
    auto_approve_min=AUTO_APPROVE_MIN,
    manual_review_min=MANUAL_REVIEW_MIN,
    hard_reject_max=HARD_REJECT_MAX,
)


def mx_hard_rules():
    return [
        lambda ctx: (
            (ctx.provider_total_debt or 0) / max(ctx.monthly_income, 1) <= HARD_MAX_DEBT_RATIO,
            "Carga de deuda crítica: la deuda total excede el 300% del ingreso mensual",
        ),
        lambda ctx: (
            ctx.amount_requested / max(ctx.monthly_income, 1) <= HARD_MAX_AMOUNT_MULTIPLIER,
            "Monto solicitado excede 12x el ingreso mensual",
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


MX_CONFIG = {
    "country_code": "MX",
    "factors": MX_FACTORS,
    "thresholds": MX_THRESHOLDS,
    "hard_rules": mx_hard_rules,
    "currency": "MXN",
    "document_type": "CURP",
}
