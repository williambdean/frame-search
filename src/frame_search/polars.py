import polars as pl

from frame_search.extension import BaseSearchAccessor


@pl.api.register_dataframe_namespace("search")
class DataFrameSearchAccessor(BaseSearchAccessor):
    """Polars DataFrame search extension."""


@pl.api.register_lazyframe_namespace("search")
class LazyFrameSearchAccessor(BaseSearchAccessor):
    """Polars LazyFrame search extension."""
