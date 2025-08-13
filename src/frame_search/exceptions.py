
class UnknownSearchColumnError(Exception):
    """Exception raised when an unknown search column is referenced."""

    def __init__(self, key):
        self.key = key
        super().__init__(f"Column {key!r} not found in schema or mapping.")


class EmptySearchQueryError(Exception):
    """Exception raised when an empty search query is provided."""

    def __init__(self):
        super().__init__("Search query cannot be empty.")

