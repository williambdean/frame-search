import importlib.util

from frame_search.search import parse_search_query, create_search


if importlib.util.find_spec("pandas") is not None:
    import frame_search.pandas  # noqa: F401

if importlib.util.find_spec("polars") is not None:
    import frame_search.polars  # noqa: F401


__all__ = [
    "parse_search_query",
    "create_search",
]
