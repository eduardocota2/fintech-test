from app.integrations.banking.base import BankingProvider
from app.integrations.banking.co_provider import ColombiaBankingProvider
from app.integrations.banking.mx_provider import MexicoBankingProvider

_providers: dict[str, BankingProvider] = {
    'CO': ColombiaBankingProvider(),
    'MX': MexicoBankingProvider(),
}

def get_banking_provider(country_code: str) -> BankingProvider:
    code = country_code.upper()
    if code not in _providers:
        raise ValueError(f'No se encontró un proveedor bancario para el código de país: {country_code}')
    return _providers[code]