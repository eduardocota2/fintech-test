import pytest

from app.db.utils.enums import ApplicationStatus
from app.domain.countries.base import CountryContext
from app.domain.countries.co import ColombiaRuleService
from app.domain.countries.mx import MexicoRuleService
from app.domain.workflows.transitions import can_transition, get_valid_transitions


def test_mx_invalid_document_is_rejected_early() -> None:
    service = MexicoRuleService()
    context = CountryContext(
        country_code="MX",
        document_id="invalid",
        monthly_income=25000,
        amount_requested=50000,
        provider_total_debt=10000,
        provider_score_hint=700,
    )

    result = service.validate(context)

    assert result.is_valid is False
    assert result.needs_manual_review is False
    assert "CURP" in (result.reason or "")
    assert result.scoring_details is None


def test_co_invalid_document_is_rejected_early() -> None:
    service = ColombiaRuleService()
    context = CountryContext(
        country_code="CO",
        document_id="ABC123",
        monthly_income=2_000_000,
        amount_requested=3_000_000,
        provider_total_debt=100_000,
        provider_score_hint=700,
    )

    result = service.validate(context)

    assert result.is_valid is False
    assert result.needs_manual_review is False
    assert "CC" in (result.reason or "")
    assert result.scoring_details is None


@pytest.mark.parametrize(
    "country,service,document_id,monthly_income,amount_requested,provider_score_hint",
    [
        ("MX", MexicoRuleService(), "AECD900101HSLHRS12", 30_000, 60_000, 850),
        ("CO", ColombiaRuleService(), "12345678", 3_500_000, 4_000_000, 900),
    ],
)
def test_country_services_return_scoring_payload_for_valid_documents(
    country: str,
    service,
    document_id: str,
    monthly_income: float,
    amount_requested: float,
    provider_score_hint: int,
) -> None:
    context = CountryContext(
        country_code=country,
        document_id=document_id,
        monthly_income=monthly_income,
        amount_requested=amount_requested,
        provider_total_debt=0,
        provider_score_hint=provider_score_hint,
    )

    result = service.validate(context)

    assert result.scoring_details is not None
    assert result.scoring_details["decision"] in {"approved_auto", "manual_review", "rejected"}
    assert isinstance(result.scoring_details["score"], (int, float))


@pytest.mark.parametrize(
    "country,service,document_id,monthly_income,amount_requested,min_score,reason_fragment",
    [
        (
            "MX",
            MexicoRuleService(),
            "AECD900101HSLHRS12",
            30_000,
            50_000,
            200,
            "Score",
        ),
        (
            "CO",
            ColombiaRuleService(),
            "1234567890",
            3_000_000,
            4_000_000,
            200,
            "Score",
        ),
    ],
)
def test_country_services_hard_rule_rejects_critical_credit_score(
    country: str,
    service,
    document_id: str,
    monthly_income: float,
    amount_requested: float,
    min_score: int,
    reason_fragment: str,
) -> None:
    context = CountryContext(
        country_code=country,
        document_id=document_id,
        monthly_income=monthly_income,
        amount_requested=amount_requested,
        provider_total_debt=0,
        provider_score_hint=min_score,
    )

    result = service.validate(context)

    assert result.is_valid is False
    assert result.needs_manual_review is False
    assert reason_fragment in (result.reason or "")


def test_workflow_transitions_fundamental_path() -> None:
    valid_from_submitted = get_valid_transitions("MX", ApplicationStatus.SUBMITTED)
    assert valid_from_submitted == (ApplicationStatus.EVALUATING,)

    assert can_transition("MX", ApplicationStatus.EVALUATING, ApplicationStatus.APPROVED) is True
    assert can_transition("CO", ApplicationStatus.EVALUATING, ApplicationStatus.REJECTED) is True
    assert can_transition("CO", ApplicationStatus.SUBMITTED, ApplicationStatus.APPROVED) is False
