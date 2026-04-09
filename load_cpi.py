"""Load CPI (inflation) data from Bank of Canada into PostgresSQL"""

import requests
import psycopg2

# CPI series available from Bank of Canada Valet API
CPI_SERIES = {
    "STATIC_TOTALCPICHANGE": "CPI All-items (% change)",
    "STATIC_CPIXFET": "CPI-trim (core inflation)",
    "STATIC_CPIMEDIAN": "CPI-median (core inflation)"
}

conn = psycopg2.connect(
    host = "localhost",
    port = 5432,
    database = "airflow",
    user = "airflow",
    password = "airflow",
)
cur = conn.cursor()

# Fetch and load each CPI series
for series_code, series_name in CPI_SERIES.items():
    url = f"https://www.bankofcanada.ca/valet/observations/{series_code}/json"
    params = {"start_date": "2024-01-01", "end_date": "2025-03-19"}

    print(f"Fetching {series_name}...")
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    count = 0
    for obs in data.get("observations", []):
        value = obs.get(series_code, {}).get("v")
        if value:
            # Add value to dim_dates if it doesn't exist
            cur.execute("""
                INSERT INTO dim_dates (date_id, year, month, month_name, day_of_week, quarter, is_weekend, is_business_day)
                VALUES (%s, EXTRACT(YEAR FROM %s::date)::int, EXTRACT(MONTH FROM %s::date)::int,
                        TO_CHAR(%s::date, 'Month'), TO_CHAR(%s::date, 'Day'),
                        EXTRACT(QUARTER FROM %s::date)::int,
                        EXTRACT(DOW FROM %s::date) IN (0,6),
                        EXTRACT(DOW FROM %s::date) NOT IN (0,6))
                ON CONFLICT (date_id) DO NOTHING
                """, (obs["d"], obs["d"], obs["d"], obs["d"], obs["d"], obs["d"], obs["d"], obs["d"]))
            
            cur.execute("""
                INSERT INTO fact_cpi (date_id, series_code, series_name, value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date_id, series_code) DO UPDATE SET value = EXCLUDED.value
            """, (obs["d"], series_code, series_name, float(value)))
            count += 1
    
    conn.commit()
    print(f"    Loaded {count} rows")

cur.execute("SELECT COUNT(*) FROM fact_cpi")
print(f"\nTotal CPI rows: {cur.fetchone()[0]}")

cur.close()
conn.close()