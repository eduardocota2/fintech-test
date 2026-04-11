from dataclasses import dataclass
from typing import Protocol, Any

@dataclass(frozen=True)
class CountryContext:
    country_code: str
    document_id: str
    monthly_income: float
    amount_requested: float
    provider_total_debt: float | None = None
    provider_score_hint: int | None = None

@dataclass(frozen=True)
class CountryRuleResult:
    is_valid: bool
    needs_manual_review: bool
    reason: str | None = None
    scoring_details: dict[str, Any] | None = None

class CountryRuleService(Protocol):
    def validate(self, context: CountryContext) -> CountryRuleResult:
        ...