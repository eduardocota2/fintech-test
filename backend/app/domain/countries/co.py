import re

from app.domain.countries.base import CountryContext, CountryResult, CountryRuleService

_CC_PATTERN = re.compile(r'^\d{6,10}$')

class ColombiaRuleService(CountryRuleService):
    def validate(self, context: CountryContext) -> CountryResult:
        if not _CC_PATTERN.match(context.document_id):
            return CountryResult(
                is_valid=False,
                needs_manual_review=False,
                reason='Formato de CC inválido'
            )
        
        # TODO: Desarrollar mejor la lógica de validación.
        debt = context.provider_total_debt or 0
        debt_ratio = debt / max(context.monthly_income, 1)
        
        if debt_ratio > 0.5:
            return CountryResult(
                is_valid=False,
                needs_manual_review=False,
                reason='Relación deuda/ingreso no permitida'
            )
        
        return CountryResult(True, False)