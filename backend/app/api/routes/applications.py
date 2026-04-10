from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.utils.enums import CountryCode
from app.db.utils.enums import ApplicationStatus
from app.db.models.loan_application import LoanApplication
from app.db.models.user import User
from app.api.schemas.loan import (
    LoanCreateRequest,
    LoanListItem,
    LoanListResponse,
    LoanResponse,
    LoanStatusUpdateRequest,
)
from app.api.dependencies.auth import get_current_admin, get_current_user
from app.services.application_service import ApplicationService
from app.services.errors import ForbiddenError, NotFoundError

router = APIRouter(prefix="/applications", tags=["applications"])


def _mask_document_id(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


def _to_loan_response(item: LoanApplication) -> LoanResponse:
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
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_application(payload: LoanCreateRequest, current_user: User = Depends(get_current_user)) -> LoanResponse:
    service = ApplicationService()
    loan = service.create_application(
        user_id=current_user.id,
        country=payload.country,
        full_name=payload.full_name,
        document_id=payload.document_id,
        amount_requested=payload.amount_requested,
        monthly_income=payload.monthly_income,
        application_date=payload.application_date,
    )

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
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ForbiddenError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return _to_loan_response(loan)


@router.get("", response_model=LoanListResponse)
def list_applications(
    country: CountryCode | None = Query(default=None),
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
) -> LoanListResponse:
    service = ApplicationService()
    items = service.list_applications(
            country=country,
            status=status_filter,
            requester_id=current_user.id,
            is_admin=current_user.is_admin,
        )

    return LoanListResponse(
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