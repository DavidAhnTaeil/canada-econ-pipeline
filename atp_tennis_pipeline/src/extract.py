"""
EXTRACT: Fetch ATP tennis data from the internet using HTTP requests.

This module teaches the fundamentals of working with APIs:
  1. Send an HTTP request to a URL
  2. Check if the request was successful
  3. Parse the response into a usable format (DataFrame)

We use the `requests` library, which is the standard way to make
HTTP calls in Python. The same pattern works for any REST API.
"""

import logging
from io import StringIO

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def fetch_csv_from_url(url: str) -> pd.DataFrame:
    """Fetch a CSV file from a URL and return it as a DataFrame.

    This is the core pattern for any API call:
      1. requests.get(url)  →  sends a GET request
      2. response.status_code  →  200 means success
      3. response.text  →  the raw data that came back

    Args:
        url: Full URL to the CSV file.

    Returns:
        DataFrame with the CSV data.

    Raises:
        requests.HTTPError: If the server returns an error (404, 500, etc.)
    """
    logger.info(f"Fetching data from: {url}")

    # Step 1: Send the HTTP GET request
    response = requests.get(url, timeout=30)

    # Step 2: Check if the request was successful
    # This raises an error if status code is 4xx or 5xx
    response.raise_for_status()

    logger.info(f"Response status: {response.status_code} (OK)")

    # Step 3: Parse the response text as CSV into a DataFrame
    # StringIO wraps the text so pandas can read it like a file
    df = pd.read_csv(StringIO(response.text))

    logger.info(f"Parsed {len(df)} rows, {len(df.columns)} columns")
    return df


def extract_players(base_url: str, path: str) -> pd.DataFrame:
    """Fetch the ATP player database.

    Contains player_id, first_name, last_name, hand, birth_date,
    country_code, and height for every ATP player in history.
    """
    url = base_url + path
    df = fetch_csv_from_url(url)

    # The player file has no header row, so we set column names manually
    df.columns = [
        "player_id", "first_name", "last_name",
        "hand", "birth_date", "country_code", "height", "wikidata_id"
    ]
    return df


def extract_rankings(base_url: str, path: str) -> pd.DataFrame:
    """Fetch current ATP rankings."""
    url = base_url + path
    df = fetch_csv_from_url(url)

    # Rankings file columns: ranking_date, rank, player_id, ranking_points
    df.columns = ["ranking_date", "rank", "player_id", "ranking_points"]
    return df


def extract_matches(base_url: str, paths: list[str]) -> pd.DataFrame:
    """Fetch match data for one or more seasons and combine them.

    This shows how to make multiple API calls and merge the results —
    a very common pattern in data engineering.
    """
    all_matches = []

    for path in paths:
        url = base_url + path
        try:
            df = fetch_csv_from_url(url)
            all_matches.append(df)
            logger.info(f"  → {len(df)} matches from {path}")
        except requests.HTTPError as e:
            logger.warning(f"  → Skipping {path}: {e}")

    if not all_matches:
        raise ValueError("No match data could be fetched!")

    combined = pd.concat(all_matches, ignore_index=True)
    logger.info(f"Total matches combined: {len(combined)}")
    return combined
