from app.domain.countries.base import CountryRuleResult
from app.integrations.banking.base import NormalizedBankProfile
from app.services.application_service import ApplicationService


class DummyProvider:
    def fetch_bank_profile(self, document_id: str, debug_debt_level: str | None = None) -> NormalizedBankProfile:
        _ = document_id
        _ = debug_debt_level
        return NormalizedBankProfile(
            bank_name="Banco Test",
            account_last4="1234",
            total_debt=12_000,
            score_hint=720,
        )


class DummyRuleService:
    def validate(self, context):
        assert context.country_code.lower() == "mx"
        assert context.document_id == "ABCD900101EFGHRS12"
        return CountryRuleResult(
            is_valid=True,
            needs_manual_review=False,
            reason="ok",
            scoring_details={"decision": "approved_auto", "score": 800},
        )


def test_evaluate_creation_orchestrates_provider_and_country_rules(monkeypatch) -> None:
    service = ApplicationService()

    monkeypatch.setattr(
        "app.services.application_service.get_banking_provider",
        lambda country_code: DummyProvider(),
    )
    monkeypatch.setattr(
        "app.services.application_service.get_country_rule_service",
        lambda country_code: DummyRuleService(),
    )

    result = service.evaluate_credit(
        country_code="mx",
        document_id="ABCD900101EFGHRS12",
        monthly_income=30_000,
        amount_requested=50_000,
        debug_debt_level="low",
    )

    assert result.country_code == "MX"
    assert result.bank_profile.bank_name == "Banco Test"
    assert result.bank_profile.account_last4 == "1234"
    assert result.rules.is_valid is True
    assert result.rules.scoring_details == {"decision": "approved_auto", "score": 800}
