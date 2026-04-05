# Money Changer Web API

![CI Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688)

Welcome to the **Money Changer Web API**, a robust, production-ready system designed to digitalize the manual recording of foreign exchange (FX) transactions for a retail store. The core tenet of this system is high reliability, precise mathematical execution, and architectural elegance utilizing modern Python design patterns.

---

## 🌟 Key Features

* **Polymorphic Domain Design:** The core of the transaction logic uses the Factory Pattern and Polymorphism. `BUY` and `SELL` operations inherit from a base `TransactionHandler`, allowing dynamic, isolated implementation of fees, spreads, and logic depending on the transaction type without heavily coupling the codebase.
* **Smart Suggestion Engine (`/suggest`):** A stateless calculation endpoint that provides precise numeric indicators to the teller on whether the customer should add more change (`customer_adds`) or if the business should eat the loss (`business_absorbs`) to hit clean, physical `0.05` cash rounding denominations.
* **Automated Third-Party Rate Syncing:** Features a built-in integration with the **Frankfurter API**. When daily rates are requested without explicit amounts, the system aggressively fetches accurate real-time data and securely caches it into the database with appropriate retail spreads attached.
* **Strict Currency Schema Validation:** Transactions and rates are protected by a native SQL `currencies` boundary. The system will aggressively block `HTTP 422` requests if a user attempts an exchange utilizing a currency not explicitly configured in the database.
* **Robust Session Fault Tolerance:** Every transaction commit is securely wrapped in global session `db.rollback()` checkpoints. In the event of a deep SQLAlchemy constraint crash or simultaneous database lock, the database gracefully recovers without corrupting the store's financial records.
* **Zero PII Footprint:** Transactions are 100% anonymized and mathematical. No customer personally identifiable information is ever routed, compiled, or persisted.

---

## 🚀 Getting Started

The project is thoroughly containerized and shipped with both Docker and Conda/vEnv compatibilities out of the box.

### Option A: Using Docker (Recommended)
Docker significantly streamlines deployment, automatically binding the ports and persisting the database gracefully.

1. **Start the API Ecosystem**
```bash
docker-compose up --build
```
*The API will instantly become available via hot-reload at `http://localhost:8000`.*

2. **Run the Database Seeder (Optional)**
If you are running the system for the very first time, initialize the dynamic `currencies` table natively through the Docker runtime:
```bash
docker-compose run --rm seed_db 
```

### Option B: Using Local Python Environment
If you prefer running natively on Mac/Linux using virtual environments (Python 3.12+ Required):

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Initialize Database and Synchronize Daily Rates**
```bash
python scripts/seed_currencies.py
python scripts/sync_rates.py
```

3. **Start FastAPI**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🛠 Project Architecture & Core Scripts

Beyond the API layer, the system includes offline operational tools:

### Automated GitHub CI/CD Pipeline
Every push to `main` instantly triggers a strict **GitHub Actions** container. It statically validates your dependencies, executes the full integration testing suite, and validates that both the Seeder and background `sync_rates` scripts connect out to the internet and parse databases without faults.

### `scripts/sync_rates.py`
A decoupled background daemon. When automated via a server Cron Job (e.g., executing at 08:00 AM daily), it maps every unique combination of supported currencies securely nested in the SQL database, computes up to *24 unique FX permutations*, queries the open markets, and automatically populates the `exchange_rates` database table ready for the tellers to use.

---

## 📖 API Documentation

FastAPI natively generates interactive, beautiful API catalogs as soon as the project boots.
To explore all schemas, try endpoints live in your browser, and review the Pydantic type constraints:

* **API Usage Guide & JSON Payloads:** [API_USAGE.md](./API_USAGE.md)
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Primary Endpoints
* `GET /api/v1/currencies` - View all supported operational currencies.
* `POST /api/v1/rates` - Upsert a daily fx rate manually or via auto-fetch.
* `POST /api/v1/transactions/suggest` - Receive highly precise rounding math suggestions for tellers.
* `POST /api/v1/transactions` - Permanently commit a transaction, computing the loss/spread and caching an immutable `effective_rate` snapshot against the active daily constraints.

---

## 🧪 Running Tests

The ecosystem relies on an isolated `conftest.py` fixture suite. It dynamically creates ephemeral SQLite in-memory tables independent of your operational configurations to secure the integrity of 50+ strict integration tests.

```bash
# Execute the test suite
pytest tests/ -v
```

*Designed meticulously for standard banking design criteria.*