from __future__ import annotations

import hashlib

from app.integrations.banking.base import NormalizedBankProfile

DEBT_LEVEL_RATIOS: dict[str, float] = {
    "low": 0.05,
    "medium": 0.45,
    "high": 0.80,
}


def get_forced_debt(level: str, debt_max: float) -> float | None:
    ratio = DEBT_LEVEL_RATIOS.get(level.lower())
    if ratio is None:
        return None
    return round(debt_max * ratio, 2)

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
        forced_debt: float | None = None,
    ) -> NormalizedBankProfile:
        cleaned_document = (document_id or "").strip().upper()
        profile_key = f"{country_code}:{cleaned_document}"

        score_ratio = _stable_ratio(profile_key + ":score")

        score_hint = int(round(_scaled_value(score_min, score_max, score_ratio)))
        
        if forced_debt is None:
            debt_ratio = _stable_ratio(f"debt:{profile_key}")
            total_debt = round(_scaled_value(debt_min, debt_max, debt_ratio), 2)
        else:
            total_debt = forced_debt

        last4 = cleaned_document[-4:] if len(cleaned_document) >= 4 else "0000"

        return NormalizedBankProfile(
            bank_name=bank_name,
            account_last4=last4,
            total_debt=total_debt,
            score_hint=score_hint,
        )