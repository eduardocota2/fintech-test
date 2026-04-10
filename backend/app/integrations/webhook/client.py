from __future__ import annotations

import httpx

from app.core.config import get_settings


class WebhookNotifier:
    def notify_status_change(self, *, application_id: str, status: str, country: str) -> None:
        settings = get_settings()
        payload = {
            "application_id": application_id,
            "status": status,
            "country": country,
        }

        timeout = httpx.Timeout(settings.webhook_timeout_seconds)
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(settings.webhook_target_url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exception:
            raise RuntimeError(f"Webhook notification failed: {exception}") from exception
