import polars as pl

from frame_search.extension import BaseSearchAccessor


@pl.api.register_dataframe_namespace("search")
class DataFrameSearchAccessor(BaseSearchAccessor):
    """Polars DataFrame search extension.

    Examples
    --------
    Example filter of a DataFrame using the search extension:

    .. code-block:: python

        import polars as pl

        import frame_search  # noqa: F401

        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "Los Angeles", "New York"]
        })

        # Using the search extension to filter
        result = df.search("York age:>30", default="city")

    Result:

    .. code-block:: text

        shape: (1, 3)
        ┌─────────┬─────┬──────────┐
        │ name    ┆ age ┆ city     │
        │ ---     ┆ --- ┆ ---      │
        │ str     ┆ i64 ┆ str      │
        ╞═════════╪═════╪══════════╡
        │ Charlie ┆ 35  ┆ New York │
        └─────────┴─────┴──────────┘

    """


@pl.api.register_lazyframe_namespace("search")
class LazyFrameSearchAccessor(BaseSearchAccessor):
    """Polars LazyFrame search extension."""
