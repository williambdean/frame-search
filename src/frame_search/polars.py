import polars as pl

from frame_search.extension import BaseSearchAccessor


@pl.api.register_dataframe_namespace("search")
class SearchAccessor(BaseSearchAccessor):
    """Polars DataFrame search extension."""
