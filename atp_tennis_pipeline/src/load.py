"""
LOAD: Save transformed data to files.

We save to both Parquet (for efficient storage and later analysis)
and CSV (so you can open it in Excel to browse the results).
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_parquet(df: pd.DataFrame, output_path: str) -> None:
    """Save DataFrame to a Parquet file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info(f"Saved {len(df)} rows to {path}")


def save_csv(df: pd.DataFrame, output_path: str) -> None:
    """Save DataFrame to a CSV file (easy to open in Excel)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved {len(df)} rows to {path}")


def print_summary(rankings_df: pd.DataFrame, stats_df: pd.DataFrame) -> None:
    """Print a human-readable summary to the console.

    This is optional but nice — after a pipeline runs, you want
    to see a quick snapshot of what the data looks like.
    """
    print("\n" + "=" * 60)
    print("  ATP TENNIS DATA SUMMARY")
    print("=" * 60)

    print("\n  📊 TOP 10 ATP RANKINGS:")
    print("  " + "-" * 56)
    for _, row in rankings_df.head(10).iterrows():
        print(
            f"  #{int(row['rank']):<4} {row['player_name']:<25} "
            f"({row['country_code']})  {int(row['ranking_points']):>6} pts"
        )

    print("\n  🏆 TOP 10 BY WIN COUNT (2024-2025):")
    print("  " + "-" * 56)
    for _, row in stats_df.head(10).iterrows():
        win_loss = f"{row['wins']}W - {row['losses']}L"
        print(
            f"  {row['player_name']:<25} {win_loss:<12} "
            f"({row['win_pct']}%)  Aces/match: {row['aces_avg']}"
        )

    print("\n  🎾 SURFACE SPECIALISTS (min 20 matches):")
    print("  " + "-" * 56)

    qualified = stats_df[stats_df["total_matches"] >= 20].copy()

    for surface, col in [("Hard", "hard_win_pct"), ("Clay", "clay_win_pct"), ("Grass", "grass_win_pct")]:
        if col in qualified.columns:
            best = qualified.nlargest(3, col)
            print(f"  Best on {surface}:")
            for _, row in best.iterrows():
                pct = row[col]
                print(f"    {row['player_name']:<25} {pct}%")

    print("\n" + "=" * 60 + "\n")
