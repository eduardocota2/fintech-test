import re

from app.domain.countries.base import CountryContext, CountryRuleResult, CountryRuleService
from app.domain.countries.config.co_config import CO_CONFIG
from app.domain.scoring.engine import Decision, ScoringEngine

_CC_PATTERN = re.compile(r"^\d{6,12}$")


class ColombiaRuleService(CountryRuleService):
    country_code = "CO"

    def __init__(self) -> None:
        self.engine = ScoringEngine(
            factors=CO_CONFIG["factors"],
            thresholds=CO_CONFIG["thresholds"],
            hard_rules=CO_CONFIG["hard_rules"](),
        )

    def validate(self, context: CountryContext) -> CountryRuleResult:
        if not _CC_PATTERN.match(context.document_id):
            return CountryRuleResult(
                is_valid=False,
                needs_manual_review=False,
                reason="CC invalida para CO",
                scoring_details=None,
            )

        result = self.engine.evaluate(context)
        is_valid = result.decision != Decision.REJECTED
        needs_review = result.decision == Decision.MANUAL_REVIEW

        if result.decision == Decision.APPROVED_AUTO:
            reason = f"Aprobacion automatica. Score: {result.score:.0f}/1000"
        elif result.decision == Decision.MANUAL_REVIEW:
            low_factors = sorted(
                [
                    (name, data["raw_score"])
                    for name, data in result.factors.items()
                    if data["raw_score"] < 600
                ],
                key=lambda item: item[1],
            )[:2]
            factor_str = ", ".join([f"{name}={score:.0f}" for name, score in low_factors])
            reason = f"Revision manual requerida. Score: {result.score:.0f}/1000"
            if factor_str:
                reason += f". Factores: {factor_str}"
        else:
            reason = result.reason or f"Rechazo por score bajo: {result.score:.0f}/1000"

        return CountryRuleResult(
            is_valid=is_valid,
            needs_manual_review=needs_review,
            reason=reason,
            scoring_details=result.to_dict(),
        )

    def explain_scoring(self, context: CountryContext) -> dict:
        return self.engine.explain(context)
