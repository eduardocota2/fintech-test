from app.db.utils.enums import ApplicationStatus
from app.domain.workflows.countries.base import CountryTransitions


CO_TRANSITIONS: CountryTransitions = {
    ApplicationStatus.SUBMITTED: (ApplicationStatus.EVALUATING,),
    ApplicationStatus.EVALUATING: (
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.PENDING_REVIEW,
    ),
    ApplicationStatus.PENDING_REVIEW: (
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
    ),
    ApplicationStatus.APPROVED: (),
    ApplicationStatus.REJECTED: (),
}
