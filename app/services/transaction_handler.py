"""
Transaction Handlers — Polymorphic Business Logic Layer

Demonstrates inheritance and polymorphism for BUY vs SELL transaction types.
Adding a new transaction type (e.g., OnlineTransaction, WholesaleTransaction)
requires only creating a new handler subclass and registering it in the factory.
"""

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction_model import TransactionModel


# ---------- Constants ----------
FEE_RATE = Decimal("0.005")          # 0.5% service fee

def get_currency_rounding_rules(currency: str) -> tuple[Decimal, Decimal]:
    """
    Returns (transaction_rounding_step, suggestion_step) for a given currency.
    - PHP: base transaction rounds to nearest 1 peso, suggestion aims for multiple of 5 pesos.
    - Default: fallback to 0.05 for both if not specified.
    """
    rules = {
        "PHP": (Decimal("1.00"), Decimal("5.00")),
        "SGD": (Decimal("0.05"), Decimal("0.05")),
        "USD": (Decimal("0.01"), Decimal("0.05")),
        "EUR": (Decimal("0.01"), Decimal("0.05")),
    }
    return rules.get(currency.upper(), (Decimal("0.05"), Decimal("0.05")))


class BaseTransactionHandler(ABC):
    """
    Abstract base class for transaction handlers.
    
    Each subclass defines HOW amounts are computed for its transaction type
    while sharing common logic (fees, rounding, ID generation).
    """

    @property
    @abstractmethod
    def side(self) -> str:
        """Return the side this handler processes ('BUY' or 'SELL')."""
        ...

    @abstractmethod
    def compute_amounts(
        self,
        rate: Decimal,
        foreign_amount: Decimal | None = None,
        base_amount: Decimal | None = None,
    ) -> dict:
        """
        Compute the transaction amounts before fee/rounding.

        Exactly one of foreign_amount or base_amount is provided.
        Returns a dict with keys: foreign_amount, base_amount, effective_rate.
        """
        ...

    # ---- shared helpers (inherited by all subclasses) ----

    def apply_fee(self, amount: Decimal) -> Decimal:
        """Calculate the service fee on a given amount."""
        return (amount * FEE_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def apply_rounding(self, amount: Decimal, base_currency: str) -> tuple[Decimal, Decimal]:
        """
        Round an amount to the nearest transaction step for the currency.
        Returns (rounded_amount, rounding_adjustment).
        """
        tx_step, _ = get_currency_rounding_rules(base_currency)
        rounded = (amount / tx_step).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * tx_step
        adjustment = rounded - amount
        return rounded, adjustment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def generate_transaction_id(self, db: Session, txn_date: date) -> str:
        """
        Generate a sequential transaction ID in format TXN-YYYYMMDD-NNNNNN.
        """
        date_str = txn_date.strftime("%Y%m%d")
        prefix = f"TXN-{date_str}-"

        # Count existing transactions for this date
        count = (
            db.query(func.count(TransactionModel.id))
            .filter(TransactionModel.transaction_id.like(f"{prefix}%"))
            .scalar()
        ) or 0

        seq = count + 1
        return f"{prefix}{seq:06d}"

    def process(
        self,
        rate: Decimal,
        base_currency: str,
        foreign_amount: Decimal | None = None,
        base_amount: Decimal | None = None,
    ) -> dict:
        """
        Full processing pipeline: compute → fee → rounding.
        Returns all computed values for storing in the transaction record.
        """
        amounts = self.compute_amounts(rate, foreign_amount, base_amount)

        # Apply fee on the base_amount (the local-currency side)
        fee = self.apply_fee(amounts["base_amount"])

        # For SELL: customer pays more base currency (add fee to base_amount)
        # For BUY: store pays less base currency (subtract fee from base_amount)
        if self.side == "SELL":
            adjusted_base = amounts["base_amount"] + fee
        else:
            adjusted_base = amounts["base_amount"] - fee

        # Round the amount given to the customer
        rounded_base, rounding_adj = self.apply_rounding(adjusted_base, base_currency)

        return {
            "foreign_amount": amounts["foreign_amount"],
            "base_amount": rounded_base,
            "effective_rate": amounts["effective_rate"],
            "fee_amount": fee,
            "rounding_adjustment": rounding_adj,
        }


class BuyTransactionHandler(BaseTransactionHandler):
    """
    BUY: Store buys foreign currency FROM the customer.
    Customer gives foreign currency → store gives base currency.
    
    Computation:
      base_amount = foreign_amount * rate
    """

    @property
    def side(self) -> str:
        return "BUY"

    def compute_amounts(
        self,
        rate: Decimal,
        foreign_amount: Decimal | None = None,
        base_amount: Decimal | None = None,
    ) -> dict:
        if foreign_amount is not None:
            computed_base = (foreign_amount * rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return {
                "foreign_amount": foreign_amount,
                "base_amount": computed_base,
                "effective_rate": rate,
            }
        else:
            # base_amount given → derive foreign_amount
            computed_foreign = (base_amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_DOWN
            )
            return {
                "foreign_amount": computed_foreign,
                "base_amount": base_amount,
                "effective_rate": rate,
            }


class SellTransactionHandler(BaseTransactionHandler):
    """
    SELL: Store sells foreign currency TO the customer.
    Customer gives base currency → store gives foreign currency.
    
    Computation:
      base_amount = foreign_amount * rate
    """

    @property
    def side(self) -> str:
        return "SELL"

    def compute_amounts(
        self,
        rate: Decimal,
        foreign_amount: Decimal | None = None,
        base_amount: Decimal | None = None,
    ) -> dict:
        if foreign_amount is not None:
            computed_base = (foreign_amount * rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return {
                "foreign_amount": foreign_amount,
                "base_amount": computed_base,
                "effective_rate": rate,
            }
        else:
            # base_amount given → derive foreign_amount
            computed_foreign = (base_amount / rate).quantize(
                Decimal("0.01"), rounding=ROUND_DOWN
            )
            return {
                "foreign_amount": computed_foreign,
                "base_amount": base_amount,
                "effective_rate": rate,
            }


class TransactionHandlerFactory:
    """
    Factory that returns the correct handler based on transaction side.
    
    To add a new transaction type (e.g., OnlineTransaction), simply:
      1. Create a new handler subclass of BaseTransactionHandler
      2. Register it in _handlers dict
    """

    _handlers: dict[str, type[BaseTransactionHandler]] = {
        "BUY": BuyTransactionHandler,
        "SELL": SellTransactionHandler,
    }

    @classmethod
    def get_handler(cls, side: str) -> BaseTransactionHandler:
        handler_cls = cls._handlers.get(side.upper())
        if handler_cls is None:
            raise ValueError(f"Unknown transaction side: '{side}'. Must be one of {list(cls._handlers.keys())}")
        return handler_cls()

    @classmethod
    def register_handler(cls, side: str, handler_cls: type[BaseTransactionHandler]) -> None:
        """Register a new handler type (extensibility point)."""
        cls._handlers[side.upper()] = handler_cls
