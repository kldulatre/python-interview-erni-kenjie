"""
Shared test fixtures — in-memory SQLite DB, FastAPI test client, sample data.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base
from app.api.deps import get_db
from app.main import app


# ---- In-memory SQLite test database ----
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh DB for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client wired to the test DB."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_rate_payload():
    """A valid exchange-rate creation payload."""
    return {
        "rate_date": "2026-02-02",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "SELL",
        "rate": "56.50",
    }


@pytest.fixture
def sample_buy_rate_payload():
    """A valid BUY exchange-rate creation payload."""
    return {
        "rate_date": "2026-02-02",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "BUY",
        "rate": "55.80",
    }
