# ATP Tennis Data Pipeline

A Python ETL project that fetches live ATP tennis data from the internet,
computes player statistics, and saves the results locally.

**What you'll learn:**
- How to make HTTP requests to fetch data (the foundation of working with APIs)
- How to clean and transform data with pandas
- How to structure a real data pipeline

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python -m src.main

# 4. Run tests
pytest tests/
```

## What the Pipeline Does

1. **EXTRACT** — Downloads three datasets from GitHub via HTTP requests:
   - ATP player database (names, nationalities, physical stats)
   - Current ATP rankings
   - Match results from 2024-2025 seasons

2. **TRANSFORM** — Cleans and enriches the data:
   - Joins rankings with player names
   - Computes win/loss records and win percentages
   - Calculates surface-specific performance (Hard, Clay, Grass)
   - Averages serve statistics (aces per match)

3. **LOAD** — Saves results to:
   - `data/output/atp_rankings.parquet` — Current rankings
   - `data/output/atp_player_stats.parquet` — Full player stats
   - `data/output/atp_summary.csv` — Same stats in CSV (open in Excel)

## How the API Part Works

We use `requests.get(url)` to fetch data, which is the exact same method
you'd use with any REST API. The pattern is always:

```python
import requests

response = requests.get("https://some-api.com/data")  # 1. Send request
response.raise_for_status()                            # 2. Check for errors
data = response.text                                   # 3. Use the response
```

The only difference with a "real" API is that you'd typically need an API key
and the data comes back as JSON instead of CSV.

## Data Source

Tennis data by [Jeff Sackmann / Tennis Abstract](https://github.com/JeffSackmann/tennis_atp),
licensed under CC BY-NC-SA 4.0.
