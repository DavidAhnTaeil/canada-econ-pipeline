# Canada Economic Data Platform

A data engineering project that fetches Canadian economic data from public APIs, processes it through automated pipelines, and visualizes the results in an interactive dashboard.

## Current Features

- **Exchange Rate Pipeline** — Fetches daily CAD exchange rates (USD, EUR, GBP, JPY, KRW) from the Bank of Canada Valet API
- **Streamlit Dashboard** — Interactive web dashboard with currency trend charts
- **Airflow Orchestration** — Scheduled DAG that runs the pipeline daily via Docker Compose
- **Dockerized** — Entire stack runs in containers (Airflow + PostgreSQL)

## Tech Stack

Python, pandas, Streamlit, Plotly, Apache Airflow, Docker, PostgreSQL

## Setup
```bash
# Run the pipeline locally
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python pipeline.py

# Run the Streamlit dashboard
streamlit run dashboard.py

# Run with Airflow (requires Docker)
docker compose up -d
# Visit http://localhost:8080 (admin/admin)
```

## Roadmap

- [ ] SQL analytics with window functions
- [ ] Star schema database design
- [ ] dbt transformation layer
- [ ] Add StatCan data (CPI, employment, GDP)
- [ ] Apache Spark for large-scale processing
- [ ] Kafka for real-time streaming
