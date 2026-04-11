from app.db.utils.enums import ApplicationStatus
from app.domain.workflows.countries.co import CO_TRANSITIONS
from app.domain.workflows.countries.mx import MX_TRANSITIONS
from backend.app.domain.workflows.countries.base import CountryTransitions


TRANSITIONS_BY_COUNTRY: dict[str, CountryTransitions] = {
    "MX": MX_TRANSITIONS,
    "CO": CO_TRANSITIONS,
}


def get_valid_transitions(
    country_code: str,
    current_status: ApplicationStatus,
) -> tuple[ApplicationStatus, ...]:
    return TRANSITIONS_BY_COUNTRY.get(country_code.upper(), {}).get(current_status, ())


def can_transition(
    country_code: str,
    from_status: ApplicationStatus,
    to_status: ApplicationStatus,
) -> bool:
    return to_status in get_valid_transitions(country_code, from_status)
