from enum import Enum

class CountryCode(str, Enum):
    MX = 'MX'
    CO = 'CO'

class ApplicationStatus(str, Enum):
    SUBMITTED = 'SUBMITTED'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

class JobType(str, Enum):
    RISK_EVALUATION = 'risk_evaluation'
    WEBHOOK_NOTIFICATION = 'webhook_notification'

class JobStatus(str, Enum):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'