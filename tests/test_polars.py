import frame_search.polars  # noqa: F401


def test_dataframe(sample_data_polars) -> None:
    assert hasattr(sample_data_polars, "search")
    assert callable(sample_data_polars.search)


def test_dataframe_lazy(sample_data_polars_lazy) -> None:
    assert hasattr(sample_data_polars_lazy, "search")
    assert callable(sample_data_polars_lazy.search)
