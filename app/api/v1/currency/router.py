from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.currency.resources import CurrencyResource
from app.schemas.currency_schema import CurrencyCreate, CurrencyResponse

router = APIRouter()
_resource = CurrencyResource()

@router.post("/", response_model=CurrencyResponse, status_code=201)
def create_currency(payload: CurrencyCreate, db: Session = Depends(get_db)):
    """Add a new supported currency."""
    return _resource.create_currency(db, payload)

@router.get("/", response_model=List[CurrencyResponse])
def list_currencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all supported currencies."""
    return _resource.list_currencies(db, skip, limit)

@router.get("/{code}", response_model=CurrencyResponse)
def get_currency(code: str, db: Session = Depends(get_db)):
    """Get a specific supported currency by its 3-letter code."""
    return _resource.get_currency(db, code)

@router.delete("/{code}", status_code=200)
def delete_currency(code: str, db: Session = Depends(get_db)):
    """Delete a supported currency."""
    _resource.delete_currency(db, code)
    return {"message": "Currency deleted successfully"}
