"""
Unit tests for the polymorphic TransactionHandler classes.
Tests the core business logic in isolation (no DB, no HTTP).
"""

import pytest
from decimal import Decimal

from app.services.transaction_handler import (
    BaseTransactionHandler,
    BuyTransactionHandler,
    SellTransactionHandler,
    TransactionHandlerFactory,
    FEE_RATE,
    ROUNDING_STEP,
)


class TestBuyTransactionHandler:

    def setup_method(self):
        self.handler = BuyTransactionHandler()

    def test_side_property(self):
        assert self.handler.side == "BUY"

    def test_compute_with_foreign_amount(self):
        result = self.handler.compute_amounts(
            rate=Decimal("55.80"),
            foreign_amount=Decimal("1000.00"),
        )
        assert result["foreign_amount"] == Decimal("1000.00")
        assert result["base_amount"] == Decimal("55800.00")
        assert result["effective_rate"] == Decimal("55.80")

    def test_compute_with_base_amount(self):
        result = self.handler.compute_amounts(
            rate=Decimal("55.80"),
            base_amount=Decimal("55800.00"),
        )
        assert result["base_amount"] == Decimal("55800.00")
        assert result["foreign_amount"] == Decimal("1000.00")

    def test_process_applies_fee_and_rounding(self):
        result = self.handler.process(
            rate=Decimal("55.80"),
            foreign_amount=Decimal("1000.00"),
        )
        # BUY: store pays less base currency (subtracts fee)
        raw_base = Decimal("55800.00")
        fee = (raw_base * FEE_RATE).quantize(Decimal("0.01"))
        assert result["fee_amount"] == fee
        assert result["effective_rate"] == Decimal("55.80")
        assert result["foreign_amount"] == Decimal("1000.00")
        # base_amount should be less than raw_base (fee subtracted + rounding)
        assert result["base_amount"] < raw_base


class TestSellTransactionHandler:

    def setup_method(self):
        self.handler = SellTransactionHandler()

    def test_side_property(self):
        assert self.handler.side == "SELL"

    def test_compute_with_foreign_amount(self):
        result = self.handler.compute_amounts(
            rate=Decimal("56.50"),
            foreign_amount=Decimal("1000.00"),
        )
        assert result["foreign_amount"] == Decimal("1000.00")
        assert result["base_amount"] == Decimal("56500.00")
        assert result["effective_rate"] == Decimal("56.50")

    def test_compute_with_base_amount(self):
        result = self.handler.compute_amounts(
            rate=Decimal("56.50"),
            base_amount=Decimal("56500.00"),
        )
        assert result["base_amount"] == Decimal("56500.00")
        assert result["foreign_amount"] == Decimal("1000.00")

    def test_process_applies_fee_and_rounding(self):
        result = self.handler.process(
            rate=Decimal("56.50"),
            foreign_amount=Decimal("1000.00"),
        )
        # SELL: customer pays more base currency (fee added)
        raw_base = Decimal("56500.00")
        fee = (raw_base * FEE_RATE).quantize(Decimal("0.01"))
        assert result["fee_amount"] == fee
        # base_amount > raw_base (fee added + rounding)
        assert result["base_amount"] > raw_base


class TestTransactionHandlerFactory:

    def test_get_buy_handler(self):
        handler = TransactionHandlerFactory.get_handler("BUY")
        assert isinstance(handler, BuyTransactionHandler)

    def test_get_sell_handler(self):
        handler = TransactionHandlerFactory.get_handler("SELL")
        assert isinstance(handler, SellTransactionHandler)

    def test_case_insensitive(self):
        handler = TransactionHandlerFactory.get_handler("buy")
        assert isinstance(handler, BuyTransactionHandler)

    def test_unknown_side_raises(self):
        with pytest.raises(ValueError, match="Unknown transaction side"):
            TransactionHandlerFactory.get_handler("HOLD")

    def test_register_custom_handler(self):
        """Demonstrate extensibility: register a new handler type."""

        class PromoTransactionHandler(BaseTransactionHandler):
            @property
            def side(self):
                return "PROMO"

            def compute_amounts(self, rate, foreign_amount=None, base_amount=None):
                # Promo: no fee, discounted rate
                discounted = rate * Decimal("0.95")
                computed_base = (foreign_amount * discounted).quantize(Decimal("0.01"))
                return {
                    "foreign_amount": foreign_amount,
                    "base_amount": computed_base,
                    "effective_rate": discounted,
                }

        TransactionHandlerFactory.register_handler("PROMO", PromoTransactionHandler)
        handler = TransactionHandlerFactory.get_handler("PROMO")
        assert isinstance(handler, PromoTransactionHandler)

        # Cleanup
        del TransactionHandlerFactory._handlers["PROMO"]


class TestSharedHelpers:
    """Test inherited helper methods (fee, rounding)."""

    def setup_method(self):
        self.handler = BuyTransactionHandler()

    def test_apply_fee(self):
        fee = self.handler.apply_fee(Decimal("10000.00"))
        expected = Decimal("50.00")  # 0.5%
        assert fee == expected

    def test_apply_fee_rounds_correctly(self):
        fee = self.handler.apply_fee(Decimal("333.33"))
        expected = Decimal("1.67")  # 333.33 * 0.005 = 1.66665 → 1.67
        assert fee == expected

    def test_apply_rounding(self):
        rounded, adj = self.handler.apply_rounding(Decimal("100.03"))
        assert rounded == Decimal("100.05")
        assert adj == Decimal("0.02")

    def test_apply_rounding_already_on_step(self):
        rounded, adj = self.handler.apply_rounding(Decimal("100.00"))
        assert rounded == Decimal("100.00")
        assert adj == Decimal("0.00")

    def test_apply_rounding_rounds_down(self):
        rounded, adj = self.handler.apply_rounding(Decimal("100.02"))
        assert rounded == Decimal("100.00")
        assert adj == Decimal("-0.02")
