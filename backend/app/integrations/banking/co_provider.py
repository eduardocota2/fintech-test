from app.integrations.banking.base import BankingProvider, NormalizedBankProfile
from app.integrations.banking.banking_profile_generator import build_bank_profile


BANK_NAME = "Banco de Colombia"
SCORE_MIN = 280
SCORE_MAX = 900
DEBT_MIN = 0.0
DEBT_MAX = 12000000.0

class ColombiaBankingProvider(BankingProvider):
    country_code = 'CO'

    def fetch_bank_profile(self, document_id: str) -> NormalizedBankProfile:
        return build_bank_profile(
            country_code=self.country_code,
            document_id=document_id,
            bank_name=BANK_NAME,
            score_min=SCORE_MIN,
            score_max=SCORE_MAX,
            debt_min=DEBT_MIN,
            debt_max=DEBT_MAX,
        )