from fastapi import HTTPException
from app.services.dummy_exchange import DummyExchange
from sqlalchemy.orm import Session
from app.models.exchange_rate_model import ExchangeRateModel
from app.schemas.exchange_rate_schema import ExchangeRateResponse, ExchangeRateGet
from datetime import datetime


class ExchangeRateResource:
    def __init__(self):
        pass

    def get_latest_exchange_rate(self, db: Session, params: ExchangeRateGet) -> ExchangeRateResponse:
        rate = db.query(ExchangeRateModel).filter(
            ExchangeRateModel.base_currency == params.base_currency, 
            ExchangeRateModel.quote_currency == params.quote_currency,
            ExchangeRateModel.rate_date == datetime.now().date()
        ).first()

        if rate is None:
            try:
                rate_value = DummyExchange().get_rate(params.base_currency, params.quote_currency)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching exchange rate: {str(e)}")

            data = ExchangeRateModel(
                base_currency=params.base_currency,
                quote_currency=params.quote_currency,
                rate=rate_value,
                rate_date=datetime.now().date(),
                side="BUY"
            )
            db.add(data)
            db.commit()
            db.refresh(data)
            return data
        
        return rate

    def delete_exchange_rate(self, id: int, db: Session) -> ExchangeRateResponse:
        rate = db.query(ExchangeRateModel).filter(ExchangeRateModel.id == id).first()
        if rate is None:
            raise HTTPException(status_code=404, detail="Exchange rate not found")
        db.delete(rate)
        db.commit()
        return rate