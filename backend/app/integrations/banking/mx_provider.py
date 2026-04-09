from app.integrations.banking.base import BankingProvider, NormalizedBankProfile

class MexicoBankingProvider(BankingProvider):
    country_code = 'MX'

    def fetch_bank_profile(self, document_id: str) -> NormalizedBankProfile:
        last4 = document_id[-4:] if len(document_id) >= 4 else '0000'
        return NormalizedBankProfile(
            bank_name='Banco de México',
            account_last4=last4,
            total_debt=3000.0,
            score_hint=720,
        )