from app.domain.countries.base import CountryRuleService
from app.domain.countries.co import ColombiaRuleService
from app.domain.countries.mx import MexicoRuleService

_country_rule_services: dict[str, CountryRuleService] = {
    'CO': ColombiaRuleService(),
    'MX': MexicoRuleService(),
}

def get_country_rule_service(country_code: str) -> CountryRuleService:
    service = _country_rule_services.get(country_code.upper())
    if not service:
        raise ValueError(f'No se encontró un servicio de reglas para el código de país: {country_code}')
    return service