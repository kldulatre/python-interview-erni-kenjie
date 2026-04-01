from typing import Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", response_model=dict)
def health_check() -> Any:
    """
    Check the health of the API.
    """
    return {"status": "ok"}
