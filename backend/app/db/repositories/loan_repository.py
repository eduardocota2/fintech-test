from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from backend.app.db.models.loan_application import LoanApplication

class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, loan_application: LoanApplication) -> LoanApplication | None:
        self.session.add(loan_application)
        return loan_application

    def get_by_id(self, application_id: str) -> LoanApplication:
        return self.session.get(LoanApplication, application_id)
    
    def list_by_filters(
            self,
            *,
            country: str | None = None,
            status: str | None = None,
    ) -> list[LoanApplication]:
        stmt: Select[tuple[LoanApplication]] = select(LoanApplication)

        if country:
            stmt = stmt.where(LoanApplication.country == country)
        if status:
            stmt = stmt.where(LoanApplication.status == status)

        stmt = stmt.order_by(LoanApplication.created_at.desc())
        return list(self.session.scalars(stmt))
