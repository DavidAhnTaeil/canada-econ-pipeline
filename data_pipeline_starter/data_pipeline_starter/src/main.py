"""Pipeline orchestrator — ties extract, transform, and load together.

Usage:
    python -m src.main
    python -m src.main --config config/pipeline_config.yaml
"""

import argparse
import logging
import time
from pathlib import Path

import yaml

from src.extract.csv_extractor import extract_csv, extract_api
from src.transform.cleaner import clean_data, add_computed_columns
from src.load.loader import load_parquet, load_sqlite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Load pipeline configuration from YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict) -> None:
    """Execute the full ETL pipeline.

    Args:
        config: Pipeline configuration dictionary.
    """
    start = time.time()
    pipeline_name = config["pipeline"]["name"]
    logger.info(f"{'='*50}")
    logger.info(f"Starting pipeline: {pipeline_name}")
    logger.info(f"{'='*50}")

    # ── EXTRACT ──────────────────────────────────────
    extract_cfg = config["extract"]
    source_type = extract_cfg["source_type"]

    if source_type == "csv":
        raw_df = extract_csv(extract_cfg["csv"]["file_path"])
    elif source_type == "api":
        api_cfg = extract_cfg["api"]
        raw_df = extract_api(api_cfg["base_url"], api_cfg["endpoint"])
    else:
        raise ValueError(f"Unknown source type: {source_type}")

    logger.info(f"Extract complete — {len(raw_df)} rows, {len(raw_df.columns)} columns")

    # ── TRANSFORM ────────────────────────────────────
    transform_cfg = config["transform"]
    clean_df = clean_data(
        raw_df,
        drop_duplicates=transform_cfg.get("drop_duplicates", True),
        drop_nulls_in=transform_cfg.get("drop_nulls_in"),
        rename_columns=transform_cfg.get("rename_columns"),
    )
    final_df = add_computed_columns(clean_df)

    logger.info(f"Transform complete — {len(final_df)} rows, {len(final_df.columns)} columns")

    # ── LOAD ─────────────────────────────────────────
    load_cfg = config["load"]
    target_type = load_cfg["target_type"]

    if target_type == "parquet":
        load_parquet(final_df, load_cfg["parquet"]["output_path"])
    elif target_type == "sqlite":
        sqlite_cfg = load_cfg["sqlite"]
        load_sqlite(final_df, sqlite_cfg["db_path"], sqlite_cfg["table_name"], sqlite_cfg["if_exists"])
    else:
        raise ValueError(f"Unknown target type: {target_type}")

    elapsed = time.time() - start
    logger.info(f"{'='*50}")
    logger.info(f"Pipeline '{pipeline_name}' finished in {elapsed:.2f}s")
    logger.info(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument(
        "--config",
        default="config/pipeline_config.yaml",
        help="Path to the pipeline config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()
