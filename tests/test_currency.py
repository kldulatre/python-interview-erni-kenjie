"""
Tests for Currency CRUD endpoints and validation.
"""
import pytest

class TestCurrency:

    def test_list_seeded_currencies(self, client):
        resp = client.get("/api/v1/currencies/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        codes = [c["code"] for c in data]
        assert "PHP" in codes
        assert "USD" in codes
        assert "EUR" in codes
        assert "SGD" in codes

    def test_create_currency(self, client):
        resp = client.post("/api/v1/currencies/", json={
            "code": "JPY",
            "name": "Japanese Yen"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "JPY"
        assert data["name"] == "Japanese Yen"

        # Try inserting again to trace conflict checking
        resp2 = client.post("/api/v1/currencies/", json={
            "code": "JPY",
            "name": "Another Yen"
        })
        assert resp2.status_code == 409

    def test_get_currency(self, client):
        resp = client.get("/api/v1/currencies/PHP")
        assert resp.status_code == 200
        assert resp.json()["code"] == "PHP"

    def test_delete_currency(self, client):
        resp = client.delete("/api/v1/currencies/SGD")
        assert resp.status_code == 200

        resp_get = client.get("/api/v1/currencies/SGD")
        assert resp_get.status_code == 404

    def test_rate_creation_fails_with_unsupported_currency(self, client):
        # We try to create a rate with KRW which is not in the db
        resp = client.post("/api/v1/rates/", json={
            "rate_date": "2026-02-02",
            "base_currency": "PHP",
            "quote_currency": "KRW",
            "side": "SELL",
            "rate": "56.50",
        })
        assert resp.status_code == 422
        assert "Unsupported currencies: KRW" in resp.json()["detail"]

    def test_suggestion_fails_with_unsupported_currency(self, client):
        resp = client.post("/api/v1/transactions/suggest", json={
            "side": "SELL",
            "base_currency": "GBP",
            "quote_currency": "USD",
            "foreign_amount": "100.00"
        })
        assert resp.status_code == 422
        assert "Unsupported currencies: GBP" in resp.json()["detail"]
