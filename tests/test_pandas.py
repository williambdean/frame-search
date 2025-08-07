import frame_search.pandas  # noqa: F401


def test_pandas(sample_data) -> None:
    assert hasattr(sample_data, "search")
    assert callable(sample_data.search)
