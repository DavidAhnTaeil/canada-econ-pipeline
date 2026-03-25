"""Unit tests for pipeline components."""

import pandas as pd
import pytest

from src.transform.cleaner import clean_data, add_computed_columns


@pytest.fixture
def sample_df():
    """Create a small test DataFrame."""
    return pd.DataFrame({
        "order_id": [1, 2, 3, 3, 4],
        "orderDate": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04"]),
        "customerName": ["Alice", "Bob", None, "Carol", "Dave"],
        "amount": [10.0, 20.0, 30.0, 30.0, None],
        "quantity": [1, 2, 3, 3, 1],
    })


class TestCleanData:
    def test_removes_duplicates(self, sample_df):
        result = clean_data(sample_df, drop_duplicates=True)
        assert len(result) == 5  # one duplicate row removed

    def test_drops_nulls_in_specified_columns(self, sample_df):
        result = clean_data(sample_df, drop_nulls_in=["amount"])
        assert result["amount"].isna().sum() == 0

    def test_renames_columns(self, sample_df):
        result = clean_data(sample_df, rename_columns={"orderDate": "order_date"})
        assert "order_date" in result.columns
        assert "orderDate" not in result.columns

    def test_no_changes_when_all_disabled(self, sample_df):
        result = clean_data(sample_df, drop_duplicates=False)
        assert len(result) == len(sample_df)


class TestAddComputedColumns:
    def test_adds_unit_price(self, sample_df):
        renamed = sample_df.rename(columns={"orderDate": "order_date"})
        result = add_computed_columns(renamed)
        assert "unit_price" in result.columns
        assert result.iloc[0]["unit_price"] == 10.0

    def test_adds_date_parts(self, sample_df):
        renamed = sample_df.rename(columns={"orderDate": "order_date"})
        result = add_computed_columns(renamed)
        assert "order_month" in result.columns
        assert "day_of_week" in result.columns
