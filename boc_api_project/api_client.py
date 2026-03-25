"""API client for the Bank of Canada Valet API.

No API key needed — this is a free public API.
The key difference from the baseball API: instead of sending
a key in the headers, we just build the right URL.
"""

import requests


BASE_URL = "https://www.bankofcanada.ca/valet"


def get_exchange_rates(currency_code: str, start_date: str, end_date: str) -> dict:
    """Fetch daily exchange rates for a currency vs CAD.

    The Valet API uses 'series names' to identify data.
    For exchange rates, the pattern is: FXCADUSD (CAD to USD)

    Args:
        currency_code: 3-letter code like 'USD', 'EUR', 'KRW'
        start_date: Start date as 'YYYY-MM-DD'
        end_date: End date as 'YYYY-MM-DD'

    Returns:
        JSON response as a dictionary.
    """
    series_name = f"FX{currency_code}CAD"
    url = f"{BASE_URL}/observations/{series_name}/json"

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    print(f"Fetching {currency_code}/CAD rates from {start_date} to {end_date}...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    print(f"  Got {len(data.get('observations', []))} data points")
    return data