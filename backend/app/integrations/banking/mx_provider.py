from app.integrations.banking.base import BankingProvider, NormalizedBankProfile
from app.integrations.banking.banking_profile_generator import build_bank_profile, get_forced_debt


BANK_NAME = "Banco de México"
SCORE_MIN = 450
SCORE_MAX = 820
DEBT_MIN = 0.0
DEBT_MAX = 120000.0

class MexicoBankingProvider(BankingProvider):
    country_code = 'MX'

    def fetch_bank_profile(
        self,
        document_id: str,
        debug_debt_level: str | None = None,
    ) -> NormalizedBankProfile:
        forced_debt = get_forced_debt(debug_debt_level, DEBT_MAX) if debug_debt_level else None

        return build_bank_profile(
            country_code=self.country_code,
            document_id=document_id,
            bank_name=BANK_NAME,
            score_min=SCORE_MIN,
            score_max=SCORE_MAX,
            debt_min=DEBT_MIN,
            debt_max=DEBT_MAX,
            forced_debt=forced_debt,
        )     