from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.utils.enums import ApplicationStatus, CountryCode

def _enum_values(enum_cls: type[CountryCode] | type[ApplicationStatus]) -> list[str]:
    return [member.value for member in enum_cls]

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    country: Mapped[CountryCode] = mapped_column(Enum(CountryCode, name="country_code"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    document_id: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_requested: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    monthly_income: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", values_callable=_enum_values),
        default=ApplicationStatus.SUBMITTED,
        nullable=False,
    )
    risk_rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="loan_applications")
    jobs = relationship("JobQueue", back_populates="loan_application")
    audit_logs = relationship("AuditLog", back_populates="loan_application")
    risk_decisions = relationship(
        "RiskDecision",
        back_populates="loan_application",
        order_by="RiskDecision.created_at.desc()",
    )