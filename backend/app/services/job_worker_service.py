from __future__ import annotations

from app.db.models.audit_log import AuditLog
from app.db.utils.enums import ApplicationStatus, JobType
from app.db.models.job_queue import JobQueue
from app.db.unit_of_work import SqlAlchemyUnitOfWork
from app.integrations.webhook.client import WebhookNotifier
from app.services.errors import NotFoundError

class JobWorkerService:
    def __init__(self) -> None:
        self.webhook_notifier = WebhookNotifier()

    def process_next_job(self) -> bool:
        with SqlAlchemyUnitOfWork() as uow:
            if uow.jobs is None:
                raise RuntimeError("JobQueue repository is not available")
            
            job = uow.jobs.claim_next_pending()
            if job is None:
                return False

            try:
                self._process_job(uow=uow, job=job)
                uow.jobs.mark_completed(job)
            except Exception as exception:
                uow.jobs.mark_failed(job, str(exception))
            
            return True


    def _process_job(self, *, uow: SqlAlchemyUnitOfWork, job: JobQueue) -> None:
        if job.job_type == JobType.RISK_EVALUATION:
            self._process_risk_evaluation_job(uow=uow, job=job)
            return
        
        if job.job_type == JobType.WEBHOOK_NOTIFICATION:
            self._process_webhook_notification(uow=uow, job=job)
            return
        
        raise NotFoundError(f"Unsupported job type: {job.job_type}")
    
    def _process_risk_evaluation_job(self, *, uow: SqlAlchemyUnitOfWork, job: JobQueue) -> None:
        if uow.loans is None or uow.audit_logs is None:
            raise RuntimeError("Loans or AuditLogs repository is not available")
        
        loan = uow.loans.get_by_id(job.loan_application_id)
        if loan is None:
            raise NotFoundError(f"Loan application not found: {job.loan_application_id}")
        
        is_valid = bool(job.payload.get("is_valid", False))
        needs_manual_review = bool(job.payload.get("needs_manual_review", False))

        if loan.status == ApplicationStatus.SUBMITTED:
            loan.status = ApplicationStatus.EVALUATING

        if not is_valid:
            loan.status = ApplicationStatus.REJECTED
            loan.risk_rating = "rejected"
        elif needs_manual_review:
            loan.status = ApplicationStatus.EVALUATING
            loan.risk_rating = ApplicationStatus.PENDING_REVIEW
        else:
            loan.status = ApplicationStatus.APPROVED
            loan.risk_rating = "auto approved"

        uow.audit_logs.add(
            AuditLog(
                loan_application_id=loan.id,
                action="risk_evaluated",
                details={
                    "status": loan.status.value,
                    "risk_rating": loan.risk_rating,
                    "job_id": job.id,
                    "user_id": loan.user_id,
                },
            )
        )

        if loan.status in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED):
            uow.jobs.add(
                JobQueue(
                    loan_application_id=loan.id,
                    job_type=JobType.WEBHOOK_NOTIFICATION,
                    payload={
                        "application_id": loan.id,
                        "status": loan.status.value,
                        "country": loan.country.value,
                    },
                )
            )

    def _process_webhook_notification(self, *, uow: SqlAlchemyUnitOfWork, job: JobQueue) -> None:
        if uow.audit_logs is None or uow.loans is None:
            raise RuntimeError("AuditLogs or Loans repository is not available")
        
        application_id = str(job.payload.get("application_id", ""))
        status = str(job.payload.get("status", ""))
        country = str(job.payload.get("country", ""))

        if not application_id or not status or not country:
            raise ValueError("Invalid payload for webhook notification job")
        
        loan = uow.loans.get_by_id(application_id)
        if loan is None:
            raise NotFoundError(f"Loan application not found: {application_id}")
        
        self.webhook_notifier.notify_status_change(
            application_id=application_id,
            status=status,
            country=country,
        )

        uow.audit_logs.add(
            AuditLog(
                loan_application_id=application_id,
                action="webhook_sent",
                details={
                    "status": status,
                    "country": country,
                    "job_id": job.id,
                    "user_id": loan.user_id,
                },
            )
        )