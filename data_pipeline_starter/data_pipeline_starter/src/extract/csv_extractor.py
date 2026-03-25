"""Extract data from various sources."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def extract_csv(file_path: str) -> pd.DataFrame:
    """Extract data from a CSV file.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Raw DataFrame from the CSV.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    df = pd.read_csv(file_path, parse_dates=["orderDate"])
    logger.info(f"Extracted {len(df)} rows from {file_path}")
    return df


def extract_api(base_url: str, endpoint: str, params: dict | None = None) -> pd.DataFrame:
    """Extract data from a REST API.

    Args:
        base_url: API base URL.
        endpoint: API endpoint path.
        params: Optional query parameters.

    Returns:
        DataFrame built from the JSON response.
    """
    import requests

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)
    logger.info(f"Extracted {len(df)} rows from {url}")
    return df
