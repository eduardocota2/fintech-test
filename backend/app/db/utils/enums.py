from enum import Enum

class CountryCode(str, Enum):
    MX = 'MX'
    CO = 'CO'

class ApplicationStatus(str, Enum):
    SUBMITTED = 'submitted'
    EVALUATING = 'evaluating'
    PENDING_REVIEW = "pending_review"
    APPROVED = 'approved'
    REJECTED = 'rejected'

class JobType(str, Enum):
    RISK_EVALUATION = 'risk_evaluation'
    WEBHOOK_NOTIFICATION = 'webhook_notification'

class JobStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'