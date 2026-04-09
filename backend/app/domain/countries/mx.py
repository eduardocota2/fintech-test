import re

from app.domain.countries.base import CountryContext, CountryResult, CountryRuleService

_CURP_PATTERN = re.compile(r'^[A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(?:0[1-9]|1[0-2])(?:[0-2][1-9]|[12]0|[31][01])[HM]{1}(?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]{1}[0-9]{1}$')


class MexicoRuleService(CountryRuleService):
    def validate(self, context: CountryContext) -> CountryResult:
        if not _CURP_PATTERN.match(context.document_id.upper()):
            return CountryResult(
                is_valid=False,
                needs_manual_review=False,
                reason='Invalid CURP format'
            )
        
        # TODO: Desarrollar mejor la lógica de validación.
        ratio = context.amount_requested / max(context.monthly_income, 1)  # Avoid division by zero
        needs_manual_review = ratio > 6
        return CountryResult(
            is_valid=True, 
            needs_manual_review=needs_manual_review
        )