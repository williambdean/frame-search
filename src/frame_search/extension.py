from frame_search import search


class BaseSearchAccessor:
    def __init__(self, obj):
        self._obj = obj

    def __call__(
        self,
        query: str,
    ):
        if query.strip() == "":
            return self._obj

        return search(self._obj, query)
