from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.utils.enums import JobStatus
from app.db.models.job_queue import JobQueue


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, job: JobQueue) -> JobQueue:
        self.session.add(job)
        return job
    
    def list_pending(self, limit: int = 10) -> list[JobQueue]:
        stmt: Select[tuple[JobQueue]] = (
            select(JobQueue)
            .where(JobQueue.status == JobStatus.PENDING)
            .order_by(JobQueue.created_at.asc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))
    
    def mark_in_progress(self, job: JobQueue) -> None:
        job.status = JobStatus.IN_PROGRESS
        job.executed_at = datetime.utcnow()

    def mark_completed(self, job: JobQueue) -> None:
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()

    def mark_failed(self, job: JobQueue, error_message: str) -> None:
        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.tries += 1