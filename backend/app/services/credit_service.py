from dataclasses import dataclass

from app.domain.countries.base import CountryContext, CountryResult
from app.domain.countries.registry import get_country_rule_service
from app.integrations.banking.base import NormalizedBankProfile
from app.integrations.banking.registry import get_banking_provider

@dataclass(frozen=True)
class CreditValidationResult:
    country_code: str
    bank_profile: NormalizedBankProfile
    rules: CountryResult


class CreditService:
    def evaluate_credit(
            self, 
            *, 
            country_code: str, 
            document_id: str, 
            monthly_income: float, 
            amount_requested: float) -> CreditValidationResult:
        
        provider = get_banking_provider(country_code)
        bank_profile = provider.fetch_bank_profile(document_id)
        context = CountryContext(
            country_code=country_code,
            document_id=document_id,
            monthly_income=monthly_income,
            amount_requested=amount_requested,
            provider_total_debt=bank_profile.total_debt,
        )

        rule_service = get_country_rule_service(country_code)
        rules = rule_service.validate(context=context)

        return CreditValidationResult(
            country_code=country_code,
            bank_profile=bank_profile,
            rules=rules,
        )