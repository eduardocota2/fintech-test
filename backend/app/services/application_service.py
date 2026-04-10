from dataclasses import dataclass

from app.domain.countries.base import CountryContext, CountryResult
from app.domain.countries.registry import get_country_rule_service
from app.integrations.banking.base import NormalizedBankProfile
from app.integrations.banking.registry import get_banking_provider
from app.db.models.loan_application import LoanApplication
from app.db.unit_of_work import SqlAlchemyUnitOfWork
from app.db.utils.enums import ApplicationStatus, CountryCode
from app.services.errors import ForbiddenError, NotFoundError

@dataclass(frozen=True)
class ApplicationValidationResult:
    country_code: str
    bank_profile: NormalizedBankProfile
    rules: CountryResult


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

        initial_status = ApplicationStatus.EVALUATING if evaluation_result.rules.is_valid else ApplicationStatus.REJECTED

        with SqlAlchemyUnitOfWork() as uow:
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
            uow.loans.create(loan)
            uow.session.flush()
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
    ) -> LoanApplication:
        with SqlAlchemyUnitOfWork() as uow:          

            loan = uow.loans.get_by_id(application_id)
            if loan is None:
                raise NotFoundError("La solicitud de préstamo no existe")

            loan.status = new_status
            uow.session.flush()
            uow.session.refresh(loan)
            return loan