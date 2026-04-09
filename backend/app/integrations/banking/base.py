from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class NormalizedBankProfile:
    bank_name: str
    account_last4: str
    total_debt: float
    score_hint: int


class BankingProvider(Protocol):
    def fetch_bank_profile(self, document_id: str) -> NormalizedBankProfile:
        ...