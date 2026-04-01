from app.services.dummy_exchange import DummyExchange
from sqlalchemy.orm import Session
from app.models.exchange_rate_model import ExchangeRateModel
from app.schemas.exchange_rate_schema import ExchangeRateResponse


class ExchangeRateResource:
    def __init__(self):
        pass

    def get_latest_exchange_rate(self, db: Session, base_currency: str, quote_currency: str) -> ExchangeRateResponse:
        rate = db.query(ExchangeRateModel).filter(
            ExchangeRateModel.base_currency == base_currency, 
            ExchangeRateModel.quote_currency == quote_currency,
            ExchangeRateModel.rate_date == datetime.now().date()
        ).first()

        if rate is None:
            rate = DummyExchange().get_rate(base_currency, quote_currency)
            data = ExchangeRateModel(
                base_currency=base_currency,
                quote_currency=quote_currency,
                rate=rate,
                rate_date=datetime.now().date()
            )
            db.add(data)
            db.commit()
            db.refresh(data)
            return data
        
        return rate
        

    def delete_exchange_rate(self, id: int) -> ExchangeRateResponse:
        rate = db.query(ExchangeRateModel).filter(ExchangeRateModel.id == id).first()
        db.delete(rate)
        db.commit()
        return rate