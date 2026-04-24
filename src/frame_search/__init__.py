import importlib.util

from .search import search, parse


if importlib.util.find_spec("pandas") is not None:
    import frame_search.pandas  # noqa: F401

if importlib.util.find_spec("polars") is not None:
    import frame_search.polars  # noqa: F401


__all__ = [
    "parse",
    "search",
]
