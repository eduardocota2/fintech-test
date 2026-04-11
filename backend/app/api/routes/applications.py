from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from typing import Annotated, Literal

from app.db.utils.enums import CountryCode
from app.db.utils.enums import ApplicationStatus
from app.db.models.loan_application import LoanApplication
from app.db.models.user import User
from app.core.config import get_settings
from app.api.schemas.loan import (
    LoanCreateRequest,
    LoanListItem,
    LoanListResponse,
    LoanResponse,
    LoanStatusUpdateRequest,
    RiskDecisionResponse,
)
from app.api.dependencies.auth import get_current_admin, get_current_user
from app.integrations.cache.application_list_cache import ApplicationListCache
from app.services.application_service import ApplicationService
from app.services.errors import ForbiddenError, NotFoundError, InvalidTransitionError

router = APIRouter(prefix="/applications", tags=["applications"])
cache = ApplicationListCache()


def _mask_document_id(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


def _to_loan_response(item: LoanApplication, latest_risk_decision=None) -> LoanResponse:
    risk_payload = None
    if latest_risk_decision is not None:
        risk_payload = RiskDecisionResponse(
            id=latest_risk_decision.id,
            loan_application_id=latest_risk_decision.loan_application_id,
            country_code=latest_risk_decision.country_code,
            decision=latest_risk_decision.decision,
            score=float(latest_risk_decision.score),
            max_possible_score=float(latest_risk_decision.max_possible_score),
            confidence=float(latest_risk_decision.confidence),
            factors=latest_risk_decision.factors,
            thresholds=latest_risk_decision.thresholds,
            reason=latest_risk_decision.reason,
            evaluated_by=latest_risk_decision.evaluated_by,
            created_at=latest_risk_decision.created_at,
        )

    return LoanResponse(
        id=item.id,
        user_id=item.user_id,
        country=item.country,
        full_name=item.full_name,
        document_id_masked=_mask_document_id(item.document_id),
        amount_requested=float(item.amount_requested),
        monthly_income=float(item.monthly_income),
        application_date=item.application_date,
        status=item.status,
        risk_rating=item.risk_rating,
        bank_name=item.bank_name,
        bank_account_last4=item.bank_account_last4,
        latest_risk_decision=risk_payload,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: LoanCreateRequest, 
    current_user: User = Depends(get_current_user),
    debug_debt_level: Annotated[
        Literal["low", "medium", "high"] | None,
        Header(alias="X-Debug-Debt-Level"),
    ] = None,
) -> LoanResponse:    
    settings = get_settings()
    if debug_debt_level is not None and not settings.enable_debug_debt_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X-Debug-Debt-Level is disabled in this environment",
        )

    service = ApplicationService()
    loan = service.create_application(
        user_id=current_user.id,
        country=payload.country,
        full_name=payload.full_name,
        document_id=payload.document_id,
        amount_requested=payload.amount_requested,
        monthly_income=payload.monthly_income,
        application_date=payload.application_date,
        debug_debt_level=debug_debt_level,
    )
    cache.bump_version()

    return _to_loan_response(loan)

@router.patch("/{application_id}/status", response_model=LoanResponse)
def update_application_status(
    application_id: str,
    payload: LoanStatusUpdateRequest,
    current_user: User = Depends(get_current_admin),
) -> LoanResponse:
    service = ApplicationService()
    try:
        loan = service.update_application_status(
            application_id=application_id,
            new_status=payload.status,
            changed_by=current_user.id,
        )
        cache.bump_version()
    except NotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except InvalidTransitionError as exception:
        raise HTTPException(status_code=400, detail=str(exception)) from exception

    return _to_loan_response(loan)

@router.get("/{application_id}", response_model=LoanResponse)
def get_application(application_id: str, current_user: User = Depends(get_current_user)) -> LoanResponse:
    service = ApplicationService()
    try:
        loan = service.get_application(
            application_id=application_id,
            requester_id=current_user.id,
            is_admin=current_user.is_admin,
        )
        latest_risk_decision = service.get_latest_risk_decision(
            application_id=application_id,
            requester_id=current_user.id,
            is_admin=current_user.is_admin,
        )
    except NotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except ForbiddenError as exception:
        raise HTTPException(status_code=403, detail=str(exception)) from exception

    return _to_loan_response(loan, latest_risk_decision=latest_risk_decision)


@router.get("", response_model=LoanListResponse)
def list_applications(
    country: CountryCode | None = Query(default=None),
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
) -> LoanListResponse:
    cached_payload = cache.get_list(
        requester_id=current_user.id,
        is_admin=current_user.is_admin,
        country=country.value if country else None,
        status_filter=status_filter.value if status_filter else None,
    )
    if cached_payload is not None:
        return LoanListResponse.model_validate(cached_payload)

    service = ApplicationService()
    items = service.list_applications(
            country=country,
            status=status_filter,
            requester_id=current_user.id,
            is_admin=current_user.is_admin,
        )

    response = LoanListResponse(
        items=[
            LoanListItem(
                id=item.id,
                country=item.country,
                full_name=item.full_name,
                amount_requested=float(item.amount_requested),
                status=item.status,
                application_date=item.application_date,
                bank_name=item.bank_name,
                bank_account_last4=item.bank_account_last4,
                created_at=item.created_at,
            )
            for item in items
        ]
    )

    cache.set_list(
        requester_id=current_user.id,
        is_admin=current_user.is_admin,
        country=country.value if country else None,
        status_filter=status_filter.value if status_filter else None,
        payload=response.model_dump(mode="json"),
    )
    return response


@router.get("/{application_id}/available-transitions", response_model=list[str])
def get_available_transitions(application_id: str, current_user: User = Depends(get_current_user)) -> list[str]:
    service = ApplicationService()
    try:
        return service.get_available_transitions(
            application_id=application_id,
            requester_id=current_user.id,
            is_admin=current_user.is_admin,
        )
    except NotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except ForbiddenError as exception:
        raise HTTPException(status_code=403, detail=str(exception)) from exception