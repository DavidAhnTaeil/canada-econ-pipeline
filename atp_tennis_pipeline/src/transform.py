"""
TRANSFORM: Clean data and compute meaningful tennis statistics.

This is where raw data becomes useful insights. We take the messy
extracted data and produce clean, analysis-ready tables.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def clean_rankings(rankings_df: pd.DataFrame, players_df: pd.DataFrame) -> pd.DataFrame:
    """Get the most recent ranking for each player and add their name.

    This demonstrates a common pattern: joining two datasets together
    to enrich one with information from the other.
    """
    # Convert ranking_date to datetime
    rankings_df["ranking_date"] = pd.to_datetime(
        rankings_df["ranking_date"], format="%Y%m%d"
    )

    # Keep only the most recent ranking date
    latest_date = rankings_df["ranking_date"].max()
    latest = rankings_df[rankings_df["ranking_date"] == latest_date].copy()
    logger.info(f"Latest ranking date: {latest_date.date()} ({len(latest)} players)")

    # Merge with player names
    # This is like a SQL JOIN — we connect rankings to players via player_id
    latest = latest.merge(
        players_df[["player_id", "first_name", "last_name", "country_code"]],
        on="player_id",
        how="left",
    )

    # Create a full name column
    latest["player_name"] = latest["first_name"] + " " + latest["last_name"]

    # Sort by rank and keep useful columns
    latest = latest.sort_values("rank").reset_index(drop=True)
    latest = latest[
        ["rank", "player_name", "country_code", "ranking_points", "player_id"]
    ]

    logger.info(f"Top ranked player: {latest.iloc[0]['player_name']}")
    return latest


def compute_player_stats(matches_df: pd.DataFrame, players_df: pd.DataFrame) -> pd.DataFrame:
    """Compute win/loss stats and surface performance for each player.

    This is a more advanced transformation using groupby and aggregation —
    skills that come up constantly in data engineering.
    """
    # --- Build a wins table ---
    # Each match has a winner_id and loser_id, so we count from both sides
    wins = (
        matches_df.groupby("winner_id")
        .agg(
            wins=("winner_id", "size"),
            aces_avg=("w_ace", "mean"),
            first_serve_pct=("w_1stIn", lambda x: _safe_serve_pct(x, matches_df.loc[x.index, "w_svpt"])),
        )
        .reset_index()
        .rename(columns={"winner_id": "player_id"})
    )

    # --- Build a losses table ---
    losses = (
        matches_df.groupby("loser_id")
        .agg(losses=("loser_id", "size"))
        .reset_index()
        .rename(columns={"loser_id": "player_id"})
    )

    # --- Merge wins and losses ---
    stats = wins.merge(losses, on="player_id", how="outer").fillna(0)
    stats["wins"] = stats["wins"].astype(int)
    stats["losses"] = stats["losses"].astype(int)
    stats["total_matches"] = stats["wins"] + stats["losses"]
    stats["win_pct"] = (stats["wins"] / stats["total_matches"] * 100).round(1)

    # --- Add surface-specific win rates ---
    surface_stats = _compute_surface_stats(matches_df)
    stats = stats.merge(surface_stats, on="player_id", how="left")

    # --- Add player names ---
    stats = stats.merge(
        players_df[["player_id", "first_name", "last_name", "country_code"]],
        on="player_id",
        how="left",
    )
    stats["player_name"] = stats["first_name"] + " " + stats["last_name"]

    # --- Clean up and sort ---
    stats = stats.sort_values("wins", ascending=False).reset_index(drop=True)
    stats["aces_avg"] = stats["aces_avg"].round(1)

    columns = [
        "player_name", "country_code", "wins", "losses", "total_matches",
        "win_pct", "aces_avg", "hard_win_pct", "clay_win_pct", "grass_win_pct",
        "player_id",
    ]
    stats = stats[[c for c in columns if c in stats.columns]]

    logger.info(f"Computed stats for {len(stats)} players")
    return stats


def _safe_serve_pct(first_in: pd.Series, serve_points: pd.Series) -> float:
    """Calculate first serve percentage, handling missing data."""
    total_in = first_in.sum()
    total_svpt = serve_points.sum()
    if total_svpt > 0:
        return round(total_in / total_svpt * 100, 1)
    return 0.0


def _compute_surface_stats(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Compute win percentage on each surface (Hard, Clay, Grass).

    This shows how to pivot data — turning rows into columns,
    which is useful whenever you want one row per entity with
    multiple metrics as columns.
    """
    surfaces = ["Hard", "Clay", "Grass"]
    all_surface_stats = []

    for surface in surfaces:
        surface_matches = matches_df[matches_df["surface"] == surface]

        if surface_matches.empty:
            continue

        # Count wins per player on this surface
        wins = (
            surface_matches.groupby("winner_id")
            .size()
            .reset_index(name="surface_wins")
            .rename(columns={"winner_id": "player_id"})
        )

        # Count losses per player on this surface
        losses = (
            surface_matches.groupby("loser_id")
            .size()
            .reset_index(name="surface_losses")
            .rename(columns={"loser_id": "player_id"})
        )

        # Combine and calculate win %
        merged = wins.merge(losses, on="player_id", how="outer").fillna(0)
        total = merged["surface_wins"] + merged["surface_losses"]
        col_name = f"{surface.lower()}_win_pct"
        merged[col_name] = (merged["surface_wins"] / total * 100).round(1)

        all_surface_stats.append(merged[["player_id", col_name]])

    if not all_surface_stats:
        return pd.DataFrame(columns=["player_id"])

    # Merge all surface stats together
    result = all_surface_stats[0]
    for df in all_surface_stats[1:]:
        result = result.merge(df, on="player_id", how="outer")

    return result
