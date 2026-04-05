# Money Changer — API Usage Guide

This guide provides practical examples on how to interact with the newly modernized Money Changer API natively using standard JSON payloads.

---

## 💡 The Smart Suggestion Engine

The `/suggest` endpoint is a stateless computational tool. It is designed to be hit continuously by the frontend application as the teller types in the desired exchange amount. It relies on the active daily exchange rate to calculate the exact spread/fee math, and suggests perfectly rounded physical cash solutions.

### Request (`POST /api/v1/transactions/suggest`)
If a customer walks in and wants to `BUY` $100 United States Dollars (`USD`) with their local Philippine Pesos (`PHP`), the teller enters the amount:

```json
{
  "side": "BUY",
  "base_currency": "PHP",
  "quote_currency": "USD",
  "foreign_amount": "100.03"
}
```

### JSON Response
The mathematical engine analyzes the daily rate, applies the base 1% markup, and calculates exactly how the 0.05 cash denomination rounding affects the business.

```json
{
  "exact_base_total": "4976.49",
  "rounded_base_total": "4976.50",
  "rounding_adjustment": "0.01",
  "fee_amount": "25.01",
  "customer_adds": "0.01",
  "business_absorbs": "0.04"
}
```
* **`customer_adds`**: The cashier should ask the customer for exactly `0.01` extra centavos to hit a clean bill note.
* **`business_absorbs`**: The store can opt to swallow `0.04` centavos of loss to hand back clean change.

---

## 🔁 Recording a Transaction

Once the teller and customer agree on the transaction outcome, you immediately persist the mathematical snapshot permanently into the ledger.

### Request (`POST /api/v1/transactions/`)

```json
{
  "timestamp": "2026-04-05T14:30:00+08:00",
  "base_currency": "PHP",
  "quote_currency": "USD",
  "side": "BUY",
  "foreign_amount": "100.03"
}
```

### JSON Response
The backend perfectly mirrors the calculation, freezes the `effective_rate` permanently so it resists daily rate fluctuations, and generates a robust audit tracking ID:

```json
{
  "transaction_id": "TXN-20260405-000001",
  "timestamp": "2026-04-05T14:30:00+08:00",
  "base_currency": "PHP",
  "quote_currency": "USD",
  "side": "BUY",
  "foreign_amount": "100.03",
  "base_amount": "4976.50",
  "effective_rate": "49.75",
  "fee_amount": "25.01",
  "rounding_adjustment": "0.01"
}
```

---

## 🗑️ Reversing a Mistake (Soft Deletion)

If the teller accidentally commits the transaction twice, they can archive it seamlessly without damaging historical database indexing schemas.

### Request (`DELETE /api/v1/transactions/{transaction_id}`)
Using the ID from the previous response:
```http
DELETE /api/v1/transactions/TXN-20260405-000001
```

### JSON Response
```json
{
  "status": "success",
  "detail": "Transaction 'TXN-20260405-000001' archived"
}
```
*The transaction is now permanently masked from daily aggregate tracking queries.*

---

## 📈 Managing Daily Exchange Rates

By default, the automated `cron_sync` background worker queries the Frankfurter API and generates these rows automatically for all your currencies. However, tellers can manually inject emergency market rates if required.

### Request (`POST /api/v1/rates/`)

```json
{
  "rate_date": "2026-04-05",
  "base_currency": "PHP",
  "quote_currency": "USD",
  "side": "SELL",
  "rate": "56.50"
}
```

> **Auto-Fetch Injection**: If you omit `"rate": "56.50"` entirely from the JSON payload above, the system will actively ping the third-party **Frankfurter API**, grab the official Inter-Bank rate, calculate the business spread, and save it automatically!

### Soft-Deleting / Restoring a Rate
* Hitting `DELETE /api/v1/rates/{id}` will trigger a soft archival.
* Executing the exact same `POST /api/v1/rates/` Upsert payload on an arched rate will **Un-Delete** the row organically and update the numerical margin. 

---

## ⚙️ Managing Supported Currencies

Our system enforces rigid Foreign Exchange constraints. If a currency does not exist in this database table, it cannot be utilized anywhere in the entire system.

### Request (`POST /api/v1/currencies/`)
```json
{
  "code": "JPY",
  "name": "Japanese Yen"
}
```
*The system instantly boots `JPY` into the active SQL mapping, allowing transactions and cross-pollination fetches immediately.*
