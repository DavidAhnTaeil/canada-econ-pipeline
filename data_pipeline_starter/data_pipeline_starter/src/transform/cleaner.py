"""Clean and transform extracted data."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def clean_data(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    drop_nulls_in: list[str] | None = None,
    rename_columns: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Apply standard cleaning steps to a DataFrame.

    Args:
        df: Raw input DataFrame.
        drop_duplicates: Whether to remove duplicate rows.
        drop_nulls_in: Columns where null values mean the row should be dropped.
        rename_columns: Mapping of old column names to new names.

    Returns:
        Cleaned DataFrame.
    """
    result = df.copy()
    initial_rows = len(result)

    # Rename columns first so downstream steps use clean names
    if rename_columns:
        result = result.rename(columns=rename_columns)
        logger.info(f"Renamed columns: {rename_columns}")

    # Drop duplicates
    if drop_duplicates:
        result = result.drop_duplicates()
        dupes_removed = initial_rows - len(result)
        if dupes_removed > 0:
            logger.info(f"Removed {dupes_removed} duplicate rows")

    # Drop rows with nulls in critical columns
    if drop_nulls_in:
        before = len(result)
        result = result.dropna(subset=drop_nulls_in)
        nulls_removed = before - len(result)
        if nulls_removed > 0:
            logger.info(f"Removed {nulls_removed} rows with nulls in {drop_nulls_in}")

    logger.info(f"Cleaning complete: {initial_rows} → {len(result)} rows")
    return result


def add_computed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add useful derived columns.

    This is where you put business logic — aggregations,
    flags, bins, date parts, etc.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with additional computed columns.
    """
    result = df.copy()

    # Example: extract date parts if a date column exists
    if "order_date" in result.columns:
        result["order_month"] = result["order_date"].dt.to_period("M").astype(str)
        result["day_of_week"] = result["order_date"].dt.day_name()

    # Example: unit price calculation
    if {"amount", "quantity"}.issubset(result.columns):
        result["unit_price"] = (result["amount"] / result["quantity"]).round(2)

    logger.info(f"Added computed columns. Total columns: {len(result.columns)}")
    return result
