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
MAX_ACCEPTABLE_DEBT_RATIO = 1.2
DEBT_CURVE = "linear"
MAX_AMOUNT_MULTIPLIER = 20
OPTIMAL_AMOUNT_MULTIPLIER = 6
CREDIT_SCORE_MIN = 300
CREDIT_SCORE_MAX = 850
CREDIT_SCORE_EXCELLENT = 750
CREDIT_SCORE_POOR = 550
MIN_STABLE_INCOME = 5000
OPTIMAL_STABLE_INCOME = 25000

# Decision thresholds
AUTO_APPROVE_MIN = 750
MANUAL_REVIEW_MIN = 550
HARD_REJECT_MAX = 550

# Hard-rule thresholds
HARD_MAX_DEBT_RATIO = 1.5
HARD_MAX_AMOUNT_MULTIPLIER = 25
HARD_MIN_CREDIT_SCORE = 350
HARD_MIN_MONTHLY_INCOME = 2000

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
            "Critical debt load: total debt exceeds 150% of monthly income",
        ),
        lambda ctx: (
            ctx.amount_requested / max(ctx.monthly_income, 1) <= HARD_MAX_AMOUNT_MULTIPLIER,
            "Requested amount exceeds 25x monthly income",
        ),
        lambda ctx: (
            (ctx.provider_score_hint or 0) >= HARD_MIN_CREDIT_SCORE,
            "Credit score is critically low",
        ),
        lambda ctx: (
            ctx.monthly_income >= HARD_MIN_MONTHLY_INCOME,
            "Monthly income below minimum threshold",
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
