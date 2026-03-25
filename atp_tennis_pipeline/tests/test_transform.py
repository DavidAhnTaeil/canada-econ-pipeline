"""Tests for the transform module."""

import pandas as pd
import pytest

from src.transform import clean_rankings, compute_player_stats


@pytest.fixture
def sample_players():
    return pd.DataFrame({
        "player_id": [1, 2, 3],
        "first_name": ["Novak", "Carlos", "Jannik"],
        "last_name": ["Djokovic", "Alcaraz", "Sinner"],
        "hand": ["R", "R", "R"],
        "birth_date": ["19870522", "20030505", "20010816"],
        "country_code": ["SRB", "ESP", "ITA"],
        "height": [188, 183, 191],
    })


@pytest.fixture
def sample_rankings():
    return pd.DataFrame({
        "ranking_date": ["20250310", "20250310", "20250310"],
        "rank": [1, 2, 3],
        "player_id": [3, 1, 2],
        "ranking_points": [11000, 9500, 8800],
    })


@pytest.fixture
def sample_matches():
    return pd.DataFrame({
        "winner_id": [1, 2, 3, 1, 2],
        "loser_id": [2, 3, 1, 3, 1],
        "surface": ["Hard", "Clay", "Hard", "Grass", "Hard"],
        "w_ace": [10, 5, 8, 12, 6],
        "w_svpt": [80, 70, 75, 85, 72],
        "w_1stIn": [50, 42, 48, 55, 44],
    })


class TestCleanRankings:
    def test_returns_latest_rankings(self, sample_rankings, sample_players):
        result = clean_rankings(sample_rankings, sample_players)
        assert len(result) == 3
        assert result.iloc[0]["player_name"] == "Jannik Sinner"
        assert result.iloc[0]["rank"] == 1

    def test_has_required_columns(self, sample_rankings, sample_players):
        result = clean_rankings(sample_rankings, sample_players)
        expected = {"rank", "player_name", "country_code", "ranking_points", "player_id"}
        assert set(result.columns) == expected


class TestComputePlayerStats:
    def test_counts_wins_and_losses(self, sample_matches, sample_players):
        result = compute_player_stats(sample_matches, sample_players)
        djokovic = result[result["player_name"] == "Novak Djokovic"].iloc[0]
        assert djokovic["wins"] == 2
        assert djokovic["losses"] == 2

    def test_calculates_win_percentage(self, sample_matches, sample_players):
        result = compute_player_stats(sample_matches, sample_players)
        djokovic = result[result["player_name"] == "Novak Djokovic"].iloc[0]
        assert djokovic["win_pct"] == 50.0
