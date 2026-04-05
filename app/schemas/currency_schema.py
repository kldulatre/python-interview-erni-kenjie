import re
from pydantic import BaseModel, field_validator, ConfigDict

class CurrencyBase(BaseModel):
    code: str
    name: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not re.match(r"^[A-Z]{3}$", v):
            raise ValueError(f"Currency code must be exactly 3 uppercase letters, got '{v}'")
        return v

class CurrencyCreate(CurrencyBase):
    """Payload for creating a new supported currency."""
    pass

class CurrencyResponse(CurrencyBase):
    """Response payload returning a currency record."""
    id: int

    model_config = ConfigDict(from_attributes=True)
