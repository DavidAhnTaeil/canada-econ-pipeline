# Data Pipeline Starter

A lightweight Python ETL (Extract → Transform → Load) project template for data engineering.

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python -m src.main
```

## Project Structure

```
data_pipeline_starter/
├── src/
│   ├── main.py              # Pipeline orchestrator
│   ├── extract/
│   │   ├── __init__.py
│   │   └── csv_extractor.py # Extract from CSV / API sources
│   ├── transform/
│   │   ├── __init__.py
│   │   └── cleaner.py       # Data cleaning & transformation
│   └── load/
│       ├── __init__.py
│       └── loader.py        # Load to Parquet / SQLite
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py     # Unit tests
├── config/
│   └── pipeline_config.yaml # Pipeline settings
├── data/                    # Sample data directory
├── requirements.txt
└── README.md
```

## Extending the Pipeline

- Add new extractors in `src/extract/` (API, database, etc.)
- Add transformation steps in `src/transform/`
- Add new load targets in `src/load/` (PostgreSQL, BigQuery, S3, etc.)
