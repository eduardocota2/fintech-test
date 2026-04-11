import re

from app.domain.countries.base import CountryContext, CountryRuleResult, CountryRuleService
from app.domain.countries.config.mx_config import MX_CONFIG
from app.domain.scoring.engine import Decision, ScoringEngine

_CURP_PATTERN = re.compile(r'^[A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(?:0[1-9]|1[0-2])(?:[0-2][1-9]|[12]0|[31][01])[HM]{1}(?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]{1}[0-9]{1}$')


class MexicoRuleService(CountryRuleService):
    country_code = "MX"

    def __init__(self) -> None:
        self.engine = ScoringEngine(
            factors=MX_CONFIG["factors"],
            thresholds=MX_CONFIG["thresholds"],
            hard_rules=MX_CONFIG["hard_rules"](),
        )

    def validate(self, context: CountryContext) -> CountryRuleResult:
        if not _CURP_PATTERN.match(context.document_id.upper()):
            return CountryRuleResult(
                is_valid=False,
                needs_manual_review=False,
                reason="CURP invalida para MX",
                scoring_details=None,
            )

        result = self.engine.evaluate(context)
        is_valid = result.decision != Decision.REJECTED
        needs_review = result.decision == Decision.MANUAL_REVIEW

        if result.decision == Decision.APPROVED_AUTO:
            reason = (
                f"Aprobacion automatica. Score: {result.score:.0f}/1000. "
                f"Supera umbral {result.thresholds['auto_approve']:.0f}."
            )
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
            reason = (
                f"Requiere revision manual. Score: {result.score:.0f}/1000 "
                f"(umbral {result.thresholds['manual_review']:.0f})."
            )
            if factor_str:
                reason += f" Factores a revisar: {factor_str}."
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
