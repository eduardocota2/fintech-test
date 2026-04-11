from __future__ import annotations

import hashlib

from app.integrations.banking.base import NormalizedBankProfile

def _stable_ratio(key: str) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    sample = int(digest[:8], 16)
    return sample / 0xFFFFFFFF

def _scaled_value(min_value: float, max_value: float, ratio: float) -> float:
    return min_value + (max_value - min_value) * ratio

def build_bank_profile(
        *,
        country_code: str,
        document_id: str,
        bank_name: str,
        score_min: int,
        score_max: int,
        debt_min: float,
        debt_max: float,
    ) -> NormalizedBankProfile:
        cleaned_document = (document_id or "").strip().upper()
        profile_key = f"{country_code}:{cleaned_document}"

        score_ratio = _stable_ratio(profile_key + ":score")
        debt_ratio = _stable_ratio(profile_key + ":debt")

        score_hint = int(round(_scaled_value(score_min, score_max, score_ratio)))
        total_debt = round(_scaled_value(debt_min, debt_max, debt_ratio), 2)

        last4 = cleaned_document[-4:] if len(cleaned_document) >= 4 else "0000"

        return NormalizedBankProfile(
            bank_name=bank_name,
            account_last4=last4,
            total_debt=total_debt,
            score_hint=score_hint,
        )