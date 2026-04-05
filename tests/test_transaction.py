"""
Tests for Transaction endpoints — integration tests that cover
rate lookup, amount computation, fee/rounding, and error handling.
"""

import pytest
from decimal import Decimal


class TestCreateTransaction:
    """POST /api/v1/transactions"""

    def _seed_rate(self, client, side="SELL", rate="56.50"):
        """Helper: create a daily rate for 2026-02-02."""
        return client.post("/api/v1/rates/", json={
            "rate_date": "2026-02-02",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": side,
            "rate": rate,
        })

    def test_sell_with_foreign_amount(self, client):
        """SELL: customer wants to buy 1000 USD. System computes PHP amount."""
        self._seed_rate(client, side="SELL", rate="56.50")

        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "1000.00",
        })
        assert resp.status_code == 201
        data = resp.json()

        assert data["transaction_id"].startswith("TXN-20260202-")
        assert data["side"] == "SELL"
        assert data["quote_currency"] == "USD"
        assert float(data["foreign_amount"]) == 1000.00
        assert float(data["effective_rate"]) == 56.50
        assert float(data["fee_amount"]) > 0  # fee was applied
        assert data["base_amount"] is not None

    def test_buy_with_foreign_amount(self, client):
        """BUY: customer sells 500 USD to the store."""
        self._seed_rate(client, side="BUY", rate="55.80")

        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "BUY",
            "foreign_amount": "500.00",
        })
        assert resp.status_code == 201
        data = resp.json()

        assert data["side"] == "BUY"
        assert float(data["foreign_amount"]) == 500.00
        assert float(data["effective_rate"]) == 55.80

    def test_sell_with_base_amount(self, client):
        """SELL: customer provides PHP 50000, wants to know how much USD they get."""
        self._seed_rate(client, side="SELL", rate="56.50")

        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "base_amount": "50000.00",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert float(data["foreign_amount"]) > 0

    def test_missing_rate_returns_422(self, client):
        """No rate set for the date → 422."""
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "1000.00",
        })
        assert resp.status_code == 422
        assert "No daily rate found" in resp.json()["detail"]

    def test_both_amounts_rejected(self, client):
        """Providing both foreign_amount and base_amount should fail."""
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "1000.00",
            "base_amount": "50000.00",
        })
        assert resp.status_code == 422

    def test_neither_amount_rejected(self, client):
        """Providing neither amount should fail."""
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
        })
        assert resp.status_code == 422

    def test_negative_amount_rejected(self, client):
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "-100.00",
        })
        assert resp.status_code == 422

    def test_invalid_currency_rejected(self, client):
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "ABCD",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "100.00",
        })
        assert resp.status_code == 422

    def test_invalid_side_rejected(self, client):
        resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "HOLD",
            "foreign_amount": "100.00",
        })
        assert resp.status_code == 422

    def test_sequential_transaction_ids(self, client):
        """Transaction IDs should increment sequentially per date."""
        self._seed_rate(client, side="SELL", rate="56.50")

        resp1 = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:00:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "100.00",
        })
        resp2 = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T11:00:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "200.00",
        })

        assert resp1.json()["transaction_id"] == "TXN-20260202-000001"
        assert resp2.json()["transaction_id"] == "TXN-20260202-000002"


class TestGetTransaction:
    """GET /api/v1/transactions/{transaction_id}"""

    def test_get_existing(self, client):
        # Seed rate and create a transaction
        client.post("/api/v1/rates/", json={
            "rate_date": "2026-02-02",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "rate": "56.50",
        })
        create_resp = client.post("/api/v1/transactions/", json={
            "timestamp": "2026-02-02T10:15:00+08:00",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": "SELL",
            "foreign_amount": "1000.00",
        })
        txn_id = create_resp.json()["transaction_id"]

        resp = client.get(f"/api/v1/transactions/{txn_id}")
        assert resp.status_code == 200
        assert resp.json()["transaction_id"] == txn_id

    def test_get_not_found(self, client):
        resp = client.get("/api/v1/transactions/TXN-99990101-000001")
        assert resp.status_code == 404


class TestListTransactions:
    """GET /api/v1/transactions"""

    def test_list_empty(self, client):
        resp = client.get("/api/v1/transactions/")
        assert resp.status_code == 200
        assert resp.json() == []


class TestSuggestionEndpoint:
    """POST /api/v1/transactions/suggest"""

    def _seed_today_rate(self, client, side="SELL", rate="50.00"):
        from datetime import datetime
        today = datetime.now().date().isoformat()
        return client.post("/api/v1/rates/", json={
            "rate_date": today,
            "base_currency": "PHP",
            "quote_currency": "USD",
            "side": side,
            "rate": rate,
        })

    def test_suggestion_round_down(self, client):
        """When rounding down, business gains/breaks even."""
        self._seed_today_rate(client, side="SELL", rate="50.00")
        resp = client.post("/api/v1/transactions/suggest", json={
            "side": "SELL",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "foreign_amount": "100.00"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["rounding_adjustment"]) == 0.0
        assert "The amount is perfectly even" in data["suggestion"]

    def test_suggestion_round_up(self, client):
        """When rounding up, business loses."""
        self._seed_today_rate(client, side="BUY", rate="50.00")
        resp = client.post("/api/v1/transactions/suggest", json={
            "side": "BUY",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "foreign_amount": "100.03"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["rounding_adjustment"]) == 0.01
        assert "Option 1" in data["suggestion"]
        assert "Option 2" in data["suggestion"]
        assert "absorbs the 0.01 loss" in data["suggestion"]

    def test_validation_errors(self, client):
        # Missing amounts
        resp1 = client.post("/api/v1/transactions/suggest", json={
            "side": "BUY",
            "base_currency": "PHP",
            "quote_currency": "USD"
        })
        assert resp1.status_code == 422

        # Both amounts supplied
        resp2 = client.post("/api/v1/transactions/suggest", json={
            "side": "BUY",
            "base_currency": "PHP",
            "quote_currency": "USD",
            "foreign_amount": "100",
            "base_amount": "5000"
        })
        assert resp2.status_code == 422
