import pytest

import pandas as pd
import polars as pl

import narwhals as nw

from frame_search import create_search


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Charlie", "David"],
            "Age": [30, 25, 35, 40],
            "Hobby": ["Reading", "Reading", "Sports", "Cooking"],
            "City of Interest": ["New York", "Los Angeles", "New York", "Charlotte"],
            "First Visit": pd.to_datetime(
                [
                    "2022-01-15",
                    "2021-06-20",
                    "2023-03-10",
                    "2020-11-05",
                ],
            ),
        }
    )


@pytest.fixture
def sample_data_polars(sample_data) -> pl.DataFrame:
    return pl.from_pandas(sample_data)


@pytest.fixture
def sample_data_polars_lazy(sample_data) -> pl.LazyFrame:
    return pl.from_pandas(sample_data).lazy()


@pytest.fixture
def search():
    return create_search(
        mapping_to_columns={
            "name": "Name",
            "age": "Age",
            "city": "City of Interest",
            "hobby": "Hobby",
            "first_visit": "First Visit",
        },
        default="Name",
        schema=nw.Schema(
            {
                "Name": nw.String,
                "Age": int,
                "Hobby": nw.String,
                "City of Interest": nw.String,
                "First Visit": nw.Datetime,
            },
        ),
    )
