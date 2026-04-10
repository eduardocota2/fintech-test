from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        return audit_log

    def list_since(self, *, created_after: datetime | None, limit: int = 50) -> list[AuditLog]:
        stmt: Select[tuple[AuditLog]] = select(AuditLog)

        if created_after is not None:
            stmt = stmt.where(AuditLog.created_at > created_after)

        stmt = stmt.order_by(AuditLog.created_at.asc()).limit(limit)
        return list(self.session.scalars(stmt))