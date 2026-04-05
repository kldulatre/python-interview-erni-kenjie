"""
Cron-compatible script to synchronize daily exchange rates.
This reads all available currencies from the DB, generates all unique pairs,
and instructs the system to fetch the daily BUY and SELL rates from the Frankfurter API.
"""
import sys
import os
import itertools
from datetime import datetime

# Ensure the app module can be found when running from the command line
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.currency_model import CurrencyModel
from app.api.v1.exchange_rate.resources import ExchangeRateResource
from app.schemas.exchange_rate_schema import ExchangeRateCreate
from fastapi import HTTPException

def sync_all_rates():
    db = SessionLocal()
    try:
        today = datetime.now().date()
        currencies = db.query(CurrencyModel.code).all()
        codes = [c[0] for c in currencies]

        if len(codes) < 2:
            print("Not enough currencies to generate pairs. Exiting.")
            return

        print(f"--- Starting Daily Exchange Rate Sync for {today} ---")
        print(f"Supported Currencies: {codes}")
        
        # Generate all permutations (A->B is different from B->A conceptually, though mathematically inverted)
        # Our app supports treating any as base vs quote.
        pairs = list(itertools.permutations(codes, 2))
        
        resource = ExchangeRateResource()
        sides = ["BUY", "SELL"]
        
        success = 0
        failed = 0
        
        for base, quote in pairs:
            for side in sides:
                print(f"Syncing: {base} to {quote} ({side})...", end=" ")
                payload = ExchangeRateCreate(
                    rate_date=today,
                    base_currency=base,
                    quote_currency=quote,
                    side=side,
                    rate=None  # Force internal fetch from 3rd party
                )
                
                try:
                    # process the rate
                    rate_obj = resource.create_or_update_rate(db, payload)
                    print(f"SUCCESS (Saved Rate: {rate_obj.rate})")
                    success += 1
                except HTTPException as e:
                    print(f"FAILED (FastAPI Error: {e.detail})")
                    failed += 1
                except Exception as e:
                    print(f"FAILED (Error: {e})")
                    failed += 1
                    
        print("-" * 50)
        print(f"Sync Complete! {success} rates synced successfully. {failed} failed.")

    finally:
        db.close()

if __name__ == "__main__":
    sync_all_rates()
