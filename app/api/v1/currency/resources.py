"""
Currency resource layer - logic for CRUD operations on supported currencies.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.currency_model import CurrencyModel
from app.schemas.currency_schema import CurrencyCreate

class CurrencyResource:

    def create_currency(self, db: Session, payload: CurrencyCreate) -> CurrencyModel:
        existing = db.query(CurrencyModel).filter(CurrencyModel.code == payload.code).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Currency '{payload.code}' already exists")
        
        new_curr = CurrencyModel(code=payload.code, name=payload.name)
        db.add(new_curr)
        db.commit()
        db.refresh(new_curr)
        return new_curr

    def list_currencies(self, db: Session, skip: int = 0, limit: int = 100) -> list[CurrencyModel]:
        return db.query(CurrencyModel).order_by(CurrencyModel.code).offset(skip).limit(limit).all()

    def get_currency(self, db: Session, code: str) -> CurrencyModel:
        curr = db.query(CurrencyModel).filter(CurrencyModel.code == code.upper()).first()
        if not curr:
            raise HTTPException(status_code=404, detail=f"Currency '{code}' not found")
        return curr

    def delete_currency(self, db: Session, code: str) -> None:
        curr = self.get_currency(db, code)
        db.delete(curr)
        db.commit()

    def validate_currencies(self, db: Session, codes: list[str]) -> None:
        codes = [c.upper() for c in set(codes)]
        found = db.query(CurrencyModel.code).filter(CurrencyModel.code.in_(codes)).all()
        found_codes = {c[0] for c in found}
        missing = set(codes) - found_codes
        if missing:
            raise HTTPException(status_code=422, detail=f"Unsupported currencies: {', '.join(missing)}")
