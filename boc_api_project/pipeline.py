"""CAD Exchange Rate Pipeline — fetch, transform, and save currency data."""

import pandas as pd
from api_client import get_exchange_rates


# Currencies we want to track against CAD
CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
}


def fetch_all_rates(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch rates for all currencies and combine into one DataFrame."""
    all_data = []

    for code, name in CURRENCIES.items():
        data = get_exchange_rates(code, start_date, end_date)
        series_key = f"FX{code}CAD"

        for obs in data["observations"]:
            all_data.append({
                "date": obs["d"],
                "currency_code": code,
                "currency_name": name,
                "rate_to_cad": float(obs[series_key]["v"]),
            })

    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["date"])
    return df


def add_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Add useful computed columns for each currency."""
    result = df.copy()

    # For each currency, calculate daily change and running stats
    enriched = []
    for code in CURRENCIES:
        currency_data = result[result["currency_code"] == code].copy()
        currency_data = currency_data.sort_values("date")

        # Daily change (%)
        currency_data["daily_change_pct"] = (
            currency_data["rate_to_cad"].pct_change() * 100
        ).round(4)

        # Rolling 5-day average
        currency_data["rolling_5d_avg"] = (
            currency_data["rate_to_cad"].rolling(window=5).mean()
        ).round(6)

        # Change from first day (%)
        first_rate = currency_data["rate_to_cad"].iloc[0]
        currency_data["change_from_start_pct"] = (
            (currency_data["rate_to_cad"] - first_rate) / first_rate * 100
        ).round(4)

        enriched.append(currency_data)

    return pd.concat(enriched, ignore_index=True)


def print_summary(df: pd.DataFrame):
    """Print a summary of the latest rates and trends."""
    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date]

    print("\n" + "=" * 60)
    print(f"  CAD EXCHANGE RATES — {latest_date.date()}")
    print("=" * 60)

    for _, row in latest.iterrows():
        direction = "▲" if row["daily_change_pct"] > 0 else "▼" if row["daily_change_pct"] < 0 else "─"
        print(
            f"  {row['currency_code']}/CAD  {row['rate_to_cad']:<12.6f}"
            f"  {direction} {row['daily_change_pct']:>+.4f}%"
            f"  (since start: {row['change_from_start_pct']:>+.4f}%)"
        )

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Fetch last 3 months of data
    START = "2025-01-01"
    END = "2025-03-19"

    print("Step 1: Fetching exchange rates...")
    df = fetch_all_rates(START, END)

    print("\nStep 2: Computing analysis...")
    df = add_analysis(df)

    print("\nStep 3: Saving results...")
    df.to_csv("exchange_rates.csv", index=False)
    print(f"  Saved {len(df)} rows to exchange_rates.csv")

    print_summary(df)
