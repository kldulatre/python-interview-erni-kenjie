from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.crud.crud_item import crud_item

router = APIRouter()

@router.get("/", response_model=List[schemas.item.Item])
def read_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    items = crud_item.get_multi(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=schemas.item.Item)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.item.ItemCreate
) -> Any:
    """
    Create a new item.
    """
    item = crud_item.create(db, obj_in=item_in)
    return item

@router.get("/{id}", response_model=schemas.item.Item)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """
    Get item by ID.
    """
    item = crud_item.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
