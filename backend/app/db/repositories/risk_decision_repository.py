from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.risk_decision import RiskDecision


class RiskDecisionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, decision: RiskDecision) -> RiskDecision:
        self.session.add(decision)
        return decision

    def get_by_loan_id(self, loan_application_id: str) -> list[RiskDecision]:
        stmt = (
            select(RiskDecision)
            .where(RiskDecision.loan_application_id == loan_application_id)
            .order_by(RiskDecision.created_at.desc())
        )
        return list(self.session.scalars(stmt))

    def get_latest(self, loan_application_id: str) -> RiskDecision | None:
        stmt = (
            select(RiskDecision)
            .where(RiskDecision.loan_application_id == loan_application_id)
            .order_by(RiskDecision.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(stmt)
