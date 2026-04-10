from fastapi import APIRouter, status

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/mock-receiver", status_code=status.HTTP_202_ACCEPTED)
def mock_webhook_receiver(payload: dict) -> dict:
    return {
        "received": True,
        "payload": payload,
    }
