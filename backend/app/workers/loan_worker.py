from __future__ import annotations

import time

from app.core.config import get_settings
from app.services.job_worker_service import JobWorkerService


def run_worker() -> None:
    settings = get_settings()
    worker = JobWorkerService()

    while True:
        processed = worker.process_next_job()
        if not processed:
            time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    run_worker()
