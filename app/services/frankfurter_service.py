"""
Service for fetching exchange rates from the Frankfurter API.
https://api.frankfurter.app/
"""

import httpx
from datetime import date
from decimal import Decimal
from fastapi import HTTPException


class FrankfurterService:
    BASE_URL = "https://api.frankfurter.app"

    def fetch_rate(self, rate_date: date, base_currency: str, quote_currency: str) -> Decimal:
        """
        Fetch the mid-market rate for a given date and currency pair.
        """
        # Frankfurter endpoint format: /YYYY-MM-DD?from=BASE&to=QUOTE
        date_str = rate_date.isoformat()
        url = f"{self.BASE_URL}/{date_str}"
        params = {
            "from": base_currency.upper(),
            "to": quote_currency.upper()
        }

        try:
            # We use a synchronous request here for simplicity,
            # though async via httpx.AsyncClient is preferred in async FastAPI workloads.
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=10.0)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=400,
                    detail=f"Rate data not available for {date_str} or unsupported currencies."
                )
            
            response.raise_for_status()
            data = response.json()

            # Ensure the quote currency is in the response rates
            quote_upper = quote_currency.upper()
            if quote_upper not in data.get("rates", {}):
                  raise HTTPException(
                    status_code=400,
                    detail=f"Quote currency {quote_upper} not found in provider response."
                )

            rate = data["rates"][quote_upper]
            return Decimal(str(rate))
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to exchange rate provider: {exc}"
            )
        except httpx.HTTPStatusError as exc:
             raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Exchange rate provider returned an error: {exc.response.text}"
            )
