from typing import Any, List
from fastapi import APIRouter, HTTPException

from app import schemas

router = APIRouter()

# Mock data for demonstration
MOCK_ITEMS = [
    {"id": 1, "title": "First Item", "description": "This is the first item", "price": 10.5, "owner_id": 123},
    {"id": 2, "title": "Second Item", "description": "Another sample item", "price": 20.0, "owner_id": 124},
]

@router.get("/", response_model=List[schemas.item.Item])
def read_items(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve items.
    """
    return MOCK_ITEMS[skip: skip + limit]

@router.post("/", response_model=schemas.item.Item)
def create_item(item_in: schemas.item.ItemCreate) -> Any:
    """
    Create a new item.
    """
    # In a real app, you would add to DB here.
    new_item = {
        "id": len(MOCK_ITEMS) + 1,
        **item_in.model_dump(),
        "owner_id": 1  # Example static owner
    }
    MOCK_ITEMS.append(new_item)
    return new_item

@router.get("/{id}", response_model=schemas.item.Item)
def read_item(id: int) -> Any:
    """
    Get item by ID.
    """
    for item in MOCK_ITEMS:
        if item["id"] == id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
