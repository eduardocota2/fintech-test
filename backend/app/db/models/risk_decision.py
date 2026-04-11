from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskDecision(Base):
    __tablename__ = "risk_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_application_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("loan_applications.id"),
        nullable=False,
        index=True,
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    max_possible_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=1000.0)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=1.0)
    factors: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    thresholds: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evaluated_by: Mapped[str] = mapped_column(String(36), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    loan_application = relationship("LoanApplication", back_populates="risk_decisions")

    def __repr__(self) -> str:
        return f"<RiskDecision(id={self.id}, decision={self.decision}, score={self.score})>"
