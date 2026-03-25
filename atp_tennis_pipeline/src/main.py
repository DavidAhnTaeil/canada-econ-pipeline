"""
ATP Tennis Data Pipeline
========================
Fetches live ATP data from the internet, transforms it into
useful statistics, and saves the results.

Usage:
    python -m src.main

What it does:
    1. EXTRACT  — Downloads player info, rankings, and match data from GitHub
    2. TRANSFORM — Cleans the data and computes stats (win %, surface performance, aces)
    3. LOAD — Saves results to Parquet + CSV and prints a summary
"""

import logging
import time

import yaml

from src.extract import extract_players, extract_rankings, extract_matches
from src.transform import clean_rankings, compute_player_stats
from src.load import save_parquet, save_csv, print_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config/pipeline_config.yaml") -> dict:
    """Load pipeline configuration from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict) -> None:
    """Execute the full ETL pipeline."""
    start = time.time()
    name = config["pipeline"]["name"]
    sources = config["sources"]
    base_url = sources["base_url"]

    logger.info("=" * 50)
    logger.info(f"Starting pipeline: {name}")
    logger.info("=" * 50)

    # ── EXTRACT ──────────────────────────────────────
    logger.info("PHASE 1: EXTRACT — Fetching data from the internet")

    players_df = extract_players(base_url, sources["players"])
    rankings_df = extract_rankings(base_url, sources["rankings"])
    matches_df = extract_matches(base_url, sources["matches"])

    logger.info(
        f"Extract done: {len(players_df)} players, "
        f"{len(rankings_df)} ranking entries, "
        f"{len(matches_df)} matches"
    )

    # ── TRANSFORM ────────────────────────────────────
    logger.info("PHASE 2: TRANSFORM — Cleaning and computing stats")

    clean_ranks = clean_rankings(rankings_df, players_df)
    player_stats = compute_player_stats(matches_df, players_df)

    logger.info(
        f"Transform done: {len(clean_ranks)} ranked players, "
        f"{len(player_stats)} players with match stats"
    )

    # ── LOAD ─────────────────────────────────────────
    logger.info("PHASE 3: LOAD — Saving results")

    output = config["output"]
    save_parquet(clean_ranks, output["rankings_file"])
    save_parquet(player_stats, output["player_stats_file"])
    save_csv(player_stats, output["summary_file"])

    # Print a nice summary to the console
    print_summary(clean_ranks, player_stats)

    elapsed = time.time() - start
    logger.info("=" * 50)
    logger.info(f"Pipeline '{name}' finished in {elapsed:.1f}s")
    logger.info("=" * 50)


if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
