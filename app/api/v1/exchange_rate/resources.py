from app.services.dummy_exchange import DummyExchange
from app.models.exchange_rate_model import ExchangeRateModel
from app.schemas.exchange_rate_schema import ExchangeRateResponse


class ExchangeRateResource:
    def __init__(self):
        pass

    def get_latest_exchange_rate(self) -> ExchangeRateResponse:
        pass

    def delete_exchange_rate(self, id: int) -> ExchangeRateResponse:
        pass