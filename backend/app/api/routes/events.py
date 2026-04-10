from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import get_current_user
from app.db.models.user import User
from app.services.event_stream_service import EventStreamService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def stream_events(current_user: User = Depends(get_current_user)) -> StreamingResponse:
    service = EventStreamService()
    stream: AsyncIterable[str] = service.stream_events(
        requester_id=current_user.id,
        is_admin=current_user.is_admin,
    )
    return StreamingResponse(stream, media_type="text/event-stream")
