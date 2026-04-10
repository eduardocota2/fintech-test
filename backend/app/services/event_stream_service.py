from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterable
from datetime import datetime

from app.core.config import get_settings
from app.db.unit_of_work import SqlAlchemyUnitOfWork

class EventStreamService:
    async def stream_events(
        self,
        *,
        requester_id: str,
        is_admin: bool,
    ) -> AsyncIterable[str]:
        cursor: datetime | None = None
        settings = get_settings()

        while True:
            with SqlAlchemyUnitOfWork() as uow:
                if uow.audit_logs is None:
                    raise RuntimeError("AuditLogs repository is not available")
                events = uow.audit_logs.list_since(created_after=cursor, limit=50)

            for event in events:
                event_user_id = event.details.get("user_id")
                if not is_admin and event_user_id != requester_id:
                    cursor = event.created_at
                    continue

                payload = {
                    "action": event.action,
                    "application_id": event.loan_application_id,
                    "details": event.details,
                    "created_at": event.created_at.isoformat(),
                }

                yield (
                    f"event: application_event\n"
                    f"id: {event.id}\n"
                    f"data: {json.dumps(payload)}\n\n"
                )
                cursor = event.created_at

            await asyncio.sleep(settings.sse_poll_seconds)