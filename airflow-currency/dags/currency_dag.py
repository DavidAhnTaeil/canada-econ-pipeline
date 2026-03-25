"""
CAD Exchange Rate DAG
Fetches daily exchange rates from the BoC API
and saves them to a CSV file.

This DAG runs every day at 2:30PM PST (after BoC publishes rates).
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
from io import StringIO
import json
import os

# Output directory inside the container
OUTPUT_DIR = "/opt/airflow/dags/data"

# Currencies to track
CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
}

def fetch_rates(**context):
    # Task 1: Fetch exchange rates from BoC API
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    all_data = []

    for code, name in CURRENCIES.items():
        url= f"https://www.bankofcanada.ca/valet/observations/FX{code}CAD/json"
        params = {"start_date":today, "end_date": today}

        print(f"Fetching {code}/CAD...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        for obs in data.get("observations", []):
            series_key = f"FX{code}CAD"
            all_data.append({
                "date":obs["d"],
                "currency": code,
                "currency_name": name,
                "rate": float(obs[series_key]["v"]),
            })

    print(f"Fetched {len(all_data)} rates")
    return all_data

def transform_and_save(**context):
    # Task 2: Transform the data and save to CSV
    # Pull data from the previous task using XCom
    raw_data = context["ti"].xcom_pull(task_ids="fetch_rates")

    if not raw_data:
        print("No data received - Bank of Canada may not have published rates yet today")
        return
    
    df = df.DataFrame(raw_data)

    # Load existing data if it exists, and append new data
    output_file = os. path.join(OUTPUT_DIR, "exchange_rates_history.csv")

    if os.path.exists(output_file):
        existing = pd.read_csv(output_file)
        df = pd.concat([existing, df]).drop_duplicates(subset=["date", "currency"], keep="last")

    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} total rows to {output_file}")

def generate_summary(**context):
    # Task 3: Print a summary of the latest rates
    output_file = os.path.join(OUTPUT_DIR, "exchange_rates_history.csv")

    if not os.path.exists(output_file):
        print("No data file found")
        return
    
    df = pd.read_csv(output_file)
    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date]

    print(f"\n{'='*50}")
    print(f"  Exchange Rates for {latest_date}")
    print(f"{'='*50}")
    for _, row in latest.iterrows():
        print(f"  {row['currency']}/CAD: {row['rate']:.6f}")
    print(f"{'='*50}")
    print(f"  Total historical records: {len(df)}")

# DAG definition
default_args = {
    "owner": "david",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="cad_exchange_rates",
    default_args=default_args,
    description="Daily CAD exchange rate pipeline from Bank of Canada",
    schedule="30 21 * * 1-5", # 2:30PM PST or 5:30PM EST (21:30 UTC), weekdays only
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=["finance", "exchange-rates"],
) as dag:
    
    task_fetch = PythonOperator(
        task_id = "fetch_rates",
        python_callable = fetch_rates,
    )

    task_transform = PythonOperator(
        task_id = "transfrom_and_save",
        python_callable = transform_and_save,
    )

    task_summary = PythonOperator(
        task_id = "generate_summary",
        python_callable = generate_summary
    )

    # Define the order: fetch -> transform -> summarize
    task_fetch >> task_transform >> task_summary