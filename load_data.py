"""Load exchange rates data directly into PostgreSQL."""

import requests
import psycopg2
from io import StringIO

CURRENCIES = ["USD","EUR","GBP","JPY","KRW"]

# Connect to the PostgreSQL running in Docker
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="airflow",
    user="airflow",
    password="airflow",
)
cur = conn.cursor()

# Fetch and insert data for each currency
for code in CURRENCIES:
    url = f"https://www.bankofcanada.ca/valet/observations/FX{code}CAD/json"
    params = {"start_date": "2024-01-01", "end_date":"2025-03-19"}

    print(f"Fetching {code}/CAD...")
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    series_key = f"FX{code}CAD"
    for obs in data["observations"]:
        cur.execute(
            """
INSERT INTO exchange_rates (rate_date, currency_code, currency_name, rate_to_cad)
VALUES (%s, %s, %s, %s)
ON CONFLICT (rate_date, currency_code) DO UPDATE SET rate_to_cad = EXCLUDED.rate_to_cad""",
(obs["d"], code, code, float(obs[series_key]["v"])),
        )

    conn.commit()
    print(f"    Loaded {code}")

cur.execute("SELECT COUNT(*) FROM exchange_rates")
total = cur.fetchone()[0]
print(f"\nTotal rows in database: {total}")

cur.close()
conn.close()