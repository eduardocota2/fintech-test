from dataclasses import dataclass

from app.domain.countries.base import CountryContext, CountryRuleResult
from app.domain.countries.registry import get_country_rule_service
from app.integrations.banking.base import NormalizedBankProfile
from app.integrations.banking.registry import get_banking_provider
from app.db.models.loan_application import LoanApplication
from app.db.models.audit_log import AuditLog
from app.db.models.job_queue import JobQueue
from app.db.models.risk_decision import RiskDecision
from app.db.unit_of_work import SqlAlchemyUnitOfWork
from app.db.utils.enums import ApplicationStatus, CountryCode, JobType
from app.services.errors import ForbiddenError, InvalidTransitionError, NotFoundError
from app.domain.workflows.transitions import can_transition, get_valid_transitions

@dataclass(frozen=True)
class ApplicationValidationResult:
    country_code: str
    bank_profile: NormalizedBankProfile
    rules: CountryRuleResult


class ApplicationService:
    def evaluate_credit(
            self, 
            *, 
            country_code: str, 
            document_id: str, 
            monthly_income: float, 
            amount_requested: float) -> ApplicationValidationResult:
        
        provider = get_banking_provider(country_code)
        bank_profile = provider.fetch_bank_profile(document_id)
        context = CountryContext(
            country_code=country_code,
            document_id=document_id,
            monthly_income=monthly_income,
            amount_requested=amount_requested,
            provider_total_debt=bank_profile.total_debt,
            provider_score_hint=bank_profile.score_hint,
        )

        rule_service = get_country_rule_service(country_code)
        rules = rule_service.validate(context=context)

        return ApplicationValidationResult(
            country_code=country_code,
            bank_profile=bank_profile,
            rules=rules,
        )
    
    def create_application(
            self,
            *,
            user_id: str,
            country: CountryCode,
            full_name: str,
            document_id: str,
            amount_requested: float,
            monthly_income: float,
            application_date) -> LoanApplication:
        
        evaluation_result = self.evaluate_credit(
            country_code=country.value,
            document_id=document_id,
            monthly_income=monthly_income,
            amount_requested=amount_requested,
        )

        initial_status = ApplicationStatus.SUBMITTED

        with SqlAlchemyUnitOfWork() as uow:
            if (
                uow.loans is None
                or uow.jobs is None
                or uow.audit_logs is None
                or uow.risk_decisions is None
                or uow.session is None
            ):
                raise RuntimeError("Repository unavailable")
            
            loan = LoanApplication(
                user_id=user_id,
                country=country,
                full_name=full_name,
                document_id=document_id,
                amount_requested=amount_requested,
                monthly_income=monthly_income,
                application_date=application_date,
                status=initial_status,
                risk_rating="manual_review" if evaluation_result.rules.needs_manual_review else "standard",
                bank_name=evaluation_result.bank_profile.bank_name,
                bank_account_last4=evaluation_result.bank_profile.account_last4,
            )
            uow.loans.add(loan)
            uow.session.flush()

            uow.jobs.add(
                JobQueue(
                    loan_application_id=loan.id,
                    job_type=JobType.RISK_EVALUATION,
                    payload={
                        "application_id": loan.id,
                        "is_valid": evaluation_result.rules.is_valid,
                        "needs_manual_review": evaluation_result.rules.needs_manual_review,
                        "reason": evaluation_result.rules.reason,
                        "scoring_details": evaluation_result.rules.scoring_details,
                    },
                )
            )

            details = evaluation_result.rules.scoring_details or {
                "decision": "rejected" if not evaluation_result.rules.is_valid else "manual_review",
                "score": 0,
                "factors": {},
                "thresholds": {},
            }
            thresholds = details.get("thresholds", {})
            factors = details.get("factors", {})
            uow.risk_decisions.add(
                RiskDecision(
                    loan_application_id=loan.id,
                    country_code=country.value,
                    decision=str(details.get("decision", "manual_review")),
                    score=float(details.get("score", 0)),
                    max_possible_score=1000.0,
                    confidence=1.0,
                    factors=factors if isinstance(factors, dict) else {},
                    thresholds=thresholds if isinstance(thresholds, dict) else {},
                    reason=evaluation_result.rules.reason,
                    evaluated_by="system",
                )
            )

            uow.audit_logs.add(
                AuditLog(
                    loan_application_id=loan.id,
                    action="application_created",
                    details={
                        "status": loan.status.value,
                        "country": loan.country.value,
                        "user_id": loan.user_id,
                    },
                )
            )

            uow.session.refresh(loan)
            return loan
        
    
    def get_application(self, *, application_id: str, requester_id: str, is_admin: bool) -> LoanApplication:
        with SqlAlchemyUnitOfWork() as uow:            
            loan = uow.loans.get_by_id(application_id)

        if loan is None:
            raise NotFoundError("La solicitud de préstamo no existe")

        if loan.user_id != requester_id and not is_admin:
            raise ForbiddenError("No tiene permisos suficientes para acceder a esta solicitud de préstamo")

        return loan
    
    def list_applications(
        self,
        *,
        country: CountryCode | None,
        status: ApplicationStatus | None,
        requester_id: str,
        is_admin: bool,
    ) -> list[LoanApplication]:
        with SqlAlchemyUnitOfWork() as uow:            
            all_items = uow.loans.list_by_filters(country=country, status=status)

        return [item for item in all_items if is_admin or item.user_id == requester_id]

    def update_application_status(
        self,
        *,
        application_id: str,
        new_status: ApplicationStatus,
        changed_by: str,
    ) -> LoanApplication:
        with SqlAlchemyUnitOfWork() as uow:
            if uow.loans is None or uow.jobs is None or uow.audit_logs is None or uow.session is None:
                raise RuntimeError("Repository unavailable")

            loan = uow.loans.get_by_id(application_id)
            if loan is None:
                raise NotFoundError("Application not found")

            old_status = loan.status
            if not can_transition(loan.country.value, old_status, new_status):
                valid = [item.value for item in get_valid_transitions(loan.country.value, old_status)]
                raise InvalidTransitionError(
                    f"Cannot transition from {old_status.value} to {new_status.value}. Valid: {valid}"
                )

            loan.status = new_status

            uow.audit_logs.add(
                AuditLog(
                    loan_application_id=loan.id,
                    action="status_transition",
                    details={
                        "from_status": old_status.value,
                        "to_status": loan.status.value,
                        "changed_by": changed_by,
                        "owner_user_id": loan.user_id,
                        "country": loan.country.value,
                    },
                )
            )

            if new_status == ApplicationStatus.EVALUATING:
                uow.jobs.add(
                    JobQueue(
                        loan_application_id=loan.id,
                        job_type=JobType.RISK_EVALUATION,
                        payload={
                            "application_id": loan.id,
                            "country": loan.country.value,
                        },
                    )
                )            

            uow.session.flush()
            uow.session.refresh(loan)
            return loan

    def get_available_transitions(
        self,
        *,
        application_id: str,
        requester_id: str,
        is_admin: bool,
    ) -> list[str]:
        loan = self.get_application(
            application_id=application_id,
            requester_id=requester_id,
            is_admin=is_admin,
        )
        return [status.value for status in get_valid_transitions(loan.country.value, loan.status)]
    
    def get_latest_risk_decision(
        self,
        *,
        application_id: str,
        requester_id: str,
        is_admin: bool,
    ) -> RiskDecision | None:        
        self.get_application(
            application_id=application_id,
            requester_id=requester_id,
            is_admin=is_admin,
        )

        with SqlAlchemyUnitOfWork() as uow:
            if uow.risk_decisions is None:
                raise RuntimeError("Repository unavailable")
            return uow.risk_decisions.get_latest(application_id)