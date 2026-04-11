from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session

from app.db.models.loan_application import LoanApplication
from app.db.utils.enums import ApplicationStatus, CountryCode

class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, loan_application: LoanApplication) -> LoanApplication | None:
        self.session.add(loan_application)
        return loan_application

    def get_by_id(self, application_id: str) -> LoanApplication:
        return self.session.get(LoanApplication, application_id)
    
    def list_by_filters(
        self,
        *,
        country: CountryCode | None = None,
        status: ApplicationStatus | None = None,
        user_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[int, list[LoanApplication]]:
        base_stmt: Select[tuple[LoanApplication]] = select(LoanApplication)

        if country:
            base_stmt = base_stmt.where(LoanApplication.country == country)
        if status:
            base_stmt = base_stmt.where(LoanApplication.status == status)
        if user_id:
            base_stmt = base_stmt.where(LoanApplication.user_id == user_id)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = int(self.session.execute(count_stmt).scalar_one())

        stmt = base_stmt.order_by(LoanApplication.created_at.desc()).limit(limit).offset(offset)
        return total, list(self.session.scalars(stmt))
