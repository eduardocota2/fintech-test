from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from app.db.repositories import AuditRepository, JobRepository, LoanRepository, UserRepository
from app.db.session import SessionLocal


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None
        self.loans: LoanRepository | None = None
        self.users: UserRepository | None = None
        self.jobs: JobRepository | None = None
        self.audit_logs: AuditRepository | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.loans = LoanRepository(self.session)
        self.users = UserRepository(self.session)
        self.jobs = JobRepository(self.session)
        self.audit_logs = AuditRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self.session is None:
            return
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of work not started")
        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of work not started")
        self.session.rollback()
