from __future__ import annotations

import logging
import time

from sqlalchemy.exc import OperationalError

from app.core.config import get_settings
from app.services.job_worker_service import JobWorkerService

logger = logging.getLogger(__name__)


def run_worker() -> None:
    settings = get_settings()
    worker = JobWorkerService()
    sleep_seconds = max(1, int(settings.worker_poll_seconds))

    while True:
        try:
            processed = worker.process_next_job()
            if not processed:
                time.sleep(sleep_seconds)
        except OperationalError as exception:
            logger.warning("Worker DB unavailable, retrying: %s", exception)
            time.sleep(sleep_seconds)
        except Exception as exception:
            logger.exception("Unexpected worker error; continuing loop")
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    run_worker()
