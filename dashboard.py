"""Interactive CAD Exchange Rate Dashboard."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from api_client import get_exchange_rates

# Page setup
st.set_page_config(page_title="CAD Exchange Rates", layout="wide")
st.title("🇨🇦 CAD Exchange Rate Dashboard")

# Sidebar — this is where user inputs go
st.sidebar.header("Settings")

CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
    "CNY": "Chinese Yuan",
    "AUD": "Australian Dollar",
    "MXN": "Mexican Peso",
}

# Let the user pick which currencies to show
selected = st.sidebar.multiselect(
    "Select currencies",
    options=list(CURRENCIES.keys()),
    default=["USD", "EUR", "KRW"],
    format_func=lambda x: f"{x} — {CURRENCIES[x]}",
)

# Let the user pick a date range
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2025-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("2025-03-19"))

# Fetch data when user clicks the button
if st.sidebar.button("Fetch Data", type="primary"):
    if not selected:
        st.warning("Please select at least one currency.")
    else:
        # Store data in session state so it persists
        all_data = []
        progress = st.progress(0, text="Fetching rates...")

        for i, code in enumerate(selected):
            data = get_exchange_rates(code, str(start_date), str(end_date))
            series_key = f"FX{code}CAD"

            for obs in data["observations"]:
                all_data.append({
                    "date": obs["d"],
                    "currency": code,
                    "rate": float(obs[series_key]["v"]),
                })
            progress.progress((i + 1) / len(selected), text=f"Fetched {code}...")

        progress.empty()
        st.session_state["df"] = pd.DataFrame(all_data)
        st.session_state["df"]["date"] = pd.to_datetime(st.session_state["df"]["date"])

# Display results if data exists
if "df" in st.session_state:
    df = st.session_state["df"]

    # --- Line Chart ---
    st.subheader("Exchange Rate Trends")
    fig = go.Figure()

    for currency in df["currency"].unique():
        currency_data = df[df["currency"] == currency]
        fig.add_trace(go.Scatter(
            x=currency_data["date"],
            y=currency_data["rate"],
            name=f"{currency}/CAD",
            mode="lines",
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Rate (per 1 CAD)",
        hovermode="x unified",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Summary Table ---
    st.subheader("Latest Rates")
    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date].copy()

    for _, row in latest.iterrows():
        currency_data = df[df["currency"] == row["currency"]].sort_values("date")
        first_rate = currency_data["rate"].iloc[0]
        change = (row["rate"] - first_rate) / first_rate * 100
        latest.loc[latest["currency"] == row["currency"], "change_pct"] = round(change, 3)

    st.dataframe(
        latest[["currency", "rate", "change_pct"]].rename(columns={
            "currency": "Currency",
            "rate": "Rate to CAD",
            "change_pct": "Change (%)",
        }),
        hide_index=True,
        use_container_width=True,
    )
