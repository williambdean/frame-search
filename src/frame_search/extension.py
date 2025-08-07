from typing import Optional

import narwhals as nw

from frame_search.search import parse_search_query


class BaseSearchAccessor:
    def __init__(self, obj):
        self._obj = obj

    def __call__(
        self,
        query: str,
        mapping_to_columns: Optional[dict[str, str]] = None,
        default: Optional[str] = None,
    ):
        if query.strip() == "":
            return self._obj

        frame = nw.from_native(self._obj)
        return frame.filter(
            parse_search_query(
                query,
                mapping_to_columns=mapping_to_columns,
                default=default,
                schema=frame.schema,
            )
        ).to_native()
