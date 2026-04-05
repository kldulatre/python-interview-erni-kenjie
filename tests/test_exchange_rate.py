"""
Tests for Exchange Rate CRUD endpoints.
"""

import pytest


class TestCreateRate:
    """POST /api/v1/rates"""

    def test_create_rate_success(self, client, sample_rate_payload):
        resp = client.post("/api/v1/rates/", json=sample_rate_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["base_currency"] == "PHP"
        assert data["quote_currency"] == "USD"
        assert data["side"] == "SELL"
        assert data["rate_date"] == "2026-02-02"
        assert float(data["rate"]) == 56.50
        assert "id" in data

    def test_create_rate_upsert(self, client, sample_rate_payload):
        """Creating the same rate twice should update, not duplicate."""
        resp1 = client.post("/api/v1/rates/", json=sample_rate_payload)
        assert resp1.status_code == 201
        id1 = resp1.json()["id"]

        # Same key, different rate value
        updated = {**sample_rate_payload, "rate": "57.00"}
        resp2 = client.post("/api/v1/rates/", json=updated)
        assert resp2.status_code == 201
        assert resp2.json()["id"] == id1  # same record
        assert float(resp2.json()["rate"]) == 57.00

    def test_create_rate_invalid_currency(self, client, sample_rate_payload):
        payload = {**sample_rate_payload, "base_currency": "ABCD"}
        resp = client.post("/api/v1/rates/", json=payload)
        assert resp.status_code == 422

    def test_create_rate_invalid_side(self, client, sample_rate_payload):
        payload = {**sample_rate_payload, "side": "HOLD"}
        resp = client.post("/api/v1/rates/", json=payload)
        assert resp.status_code == 422

    def test_create_rate_negative_rate(self, client, sample_rate_payload):
        payload = {**sample_rate_payload, "rate": "-1.00"}
        resp = client.post("/api/v1/rates/", json=payload)
        assert resp.status_code == 422

    def test_create_rate_zero_rate(self, client, sample_rate_payload):
        payload = {**sample_rate_payload, "rate": "0"}
        resp = client.post("/api/v1/rates/", json=payload)
        assert resp.status_code == 422


class TestListRates:
    """GET /api/v1/rates"""

    def test_list_empty(self, client):
        resp = client.get("/api/v1/rates/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_filters(self, client, sample_rate_payload, sample_buy_rate_payload):
        client.post("/api/v1/rates/", json=sample_rate_payload)
        client.post("/api/v1/rates/", json=sample_buy_rate_payload)

        # Filter by side
        resp = client.get("/api/v1/rates/", params={"side": "BUY"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["side"] == "BUY"

    def test_list_all(self, client, sample_rate_payload, sample_buy_rate_payload):
        client.post("/api/v1/rates/", json=sample_rate_payload)
        client.post("/api/v1/rates/", json=sample_buy_rate_payload)

        resp = client.get("/api/v1/rates/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetRate:
    """GET /api/v1/rates/{id}"""

    def test_get_existing(self, client, sample_rate_payload):
        create_resp = client.post("/api/v1/rates/", json=sample_rate_payload)
        rate_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/rates/{rate_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == rate_id

    def test_get_not_found(self, client):
        resp = client.get("/api/v1/rates/9999")
        assert resp.status_code == 404


class TestUpdateRate:
    """PUT /api/v1/rates/{id}"""

    def test_update_success(self, client, sample_rate_payload):
        create_resp = client.post("/api/v1/rates/", json=sample_rate_payload)
        rate_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/rates/{rate_id}", json={"rate": "58.00"})
        assert resp.status_code == 200
        assert float(resp.json()["rate"]) == 58.00

    def test_update_not_found(self, client):
        resp = client.put("/api/v1/rates/9999", json={"rate": "58.00"})
        assert resp.status_code == 404

    def test_update_invalid_rate(self, client, sample_rate_payload):
        create_resp = client.post("/api/v1/rates/", json=sample_rate_payload)
        rate_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/rates/{rate_id}", json={"rate": "-5.00"})
        assert resp.status_code == 422


class TestDeleteRate:
    """DELETE /api/v1/rates/{id}"""

    def test_delete_success(self, client, sample_rate_payload):
        create_resp = client.post("/api/v1/rates/", json=sample_rate_payload)
        rate_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/rates/{rate_id}")
        assert resp.status_code == 200

        # Verify deleted
        resp2 = client.get(f"/api/v1/rates/{rate_id}")
        assert resp2.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/api/v1/rates/9999")
        assert resp.status_code == 404
