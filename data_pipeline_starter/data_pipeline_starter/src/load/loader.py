"""Load transformed data to various targets."""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def load_parquet(df: pd.DataFrame, output_path: str) -> Path:
    """Write DataFrame to a Parquet file.

    Args:
        df: Transformed DataFrame to save.
        output_path: Destination file path.

    Returns:
        Path to the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(path, index=False, engine="pyarrow")
    logger.info(f"Loaded {len(df)} rows to {path}")
    return path


def load_sqlite(
    df: pd.DataFrame,
    db_path: str,
    table_name: str,
    if_exists: str = "replace",
) -> int:
    """Write DataFrame to a SQLite database table.

    Args:
        df: Transformed DataFrame to save.
        db_path: Path to the SQLite database file.
        table_name: Target table name.
        if_exists: Behavior when table exists ('replace' or 'append').

    Returns:
        Number of rows written.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{path}")
    rows = df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.info(f"Loaded {rows} rows to {table_name} in {path}")
    return rows or len(df)
