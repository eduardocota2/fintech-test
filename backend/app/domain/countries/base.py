from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class CountryContext:
    country_code: str
    document_id: str
    monthly_income: float
    amount_requested: float
    provider_total_debt: float | None = None

@dataclass(frozen=True)
class CountryResult:
    is_valid: bool
    needs_manual_review: bool
    reason: str | None = None

class CountryRuleService(Protocol):
    def validate(self, context: CountryContext) -> CountryResult:
        ...