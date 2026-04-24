import pytest

import pandas as pd
import polars as pl

from frame_search.search import create_search


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Charlie", "David"],
            "Age": [30, 25, 35, 40],
            "Hobby": ["Reading", "Reading", "Sports", "Cooking"],
            "City of Interest": ["New York", "Los Angeles", "New York", "Charlotte"],
            "seen_movie": [True, False, True, False],
            "First Visit": pd.to_datetime(
                [
                    "2022-01-15",
                    "2021-06-20",
                    "2023-03-10",
                    "2020-11-05",
                ],
            ),
            "Nickname": ["Al", None, "Chuck", None],
        }
    ).assign(
        older_than_30=lambda df: df["Age"] > 30,
    )


@pytest.fixture
def sample_data_polars(sample_data) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "Name": sample_data["Name"].tolist(),
            "Age": sample_data["Age"].tolist(),
            "Hobby": sample_data["Hobby"].tolist(),
            "City of Interest": sample_data["City of Interest"].tolist(),
            "seen_movie": sample_data["seen_movie"].tolist(),
            "First Visit": sample_data["First Visit"].tolist(),
            "older_than_30": sample_data["older_than_30"].tolist(),
            "Nickname": ["Al", None, "Chuck", None],
        }
    )


@pytest.fixture
def sample_data_polars_lazy(sample_data) -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "Name": sample_data["Name"].tolist(),
            "Age": sample_data["Age"].tolist(),
            "Hobby": sample_data["Hobby"].tolist(),
            "City of Interest": sample_data["City of Interest"].tolist(),
            "seen_movie": sample_data["seen_movie"].tolist(),
            "First Visit": sample_data["First Visit"].tolist(),
            "older_than_30": sample_data["older_than_30"].tolist(),
            "Nickname": ["Al", None, "Chuck", None],
        }
    ).lazy()


@pytest.fixture
def search():
    return create_search(
        mapping_to_columns={
            "name": "Name",
            "age": "Age",
            "hobby": "Hobby",
            "city": "City of Interest",
            "seen_movie": "seen_movie",
            "visit": "First Visit",
            "first_visit": "First Visit",
            "older_than_30": "older_than_30",
            "nickname": "Nickname",
        },
        default="Name",
    )
