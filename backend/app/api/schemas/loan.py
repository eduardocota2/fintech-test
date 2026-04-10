from datetime import date, datetime

from pydantic import BaseModel, Field

from app.db.utils.enums import ApplicationStatus, CountryCode

class LoanCreateRequest(BaseModel):
    country: CountryCode
    full_name: str = Field(..., max_length=150)
    document_id: str = Field(..., max_length=50)
    amount_requested: float = Field(..., gt=0)
    monthly_income: float = Field(..., gt=0)
    application_date: date

class LoanStatusUpdateRequest(BaseModel):
    status: ApplicationStatus
    
class LoanResponse(BaseModel):
    id: str
    user_id: str
    country: CountryCode
    full_name: str
    document_id_masked: str
    amount_requested: float
    monthly_income: float
    application_date: date
    status: ApplicationStatus
    risk_rating: str | None = None
    bank_name: str | None = None
    bank_account_last4: str | None = None
    created_at: datetime
    updated_at: datetime

class LoanListItem(BaseModel):
    id: str
    country: CountryCode
    full_name: str
    amount_requested: float
    status: ApplicationStatus
    application_date: date
    bank_name: str | None = None
    bank_account_last4: str | None = None
    created_at: datetime

class LoanListResponse(BaseModel):
    items: list[LoanListItem]