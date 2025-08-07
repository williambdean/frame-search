import frame_search.polars  # noqa: F401


def test_pandas(sample_data_polars) -> None:
    assert hasattr(sample_data_polars, "search")
    assert callable(sample_data_polars.search)
