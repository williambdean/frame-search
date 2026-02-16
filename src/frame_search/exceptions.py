class UnknownSearchColumnError(Exception):
    """Exception raised when an unknown search column is referenced."""

    def __init__(self, key):
        self.key = key
        super().__init__(f"Column {key!r} not found in schema or mapping.")


class EmptySearchQueryError(Exception):
    """Exception raised when an empty search query is provided."""

    def __init__(self):
        super().__init__("Search query cannot be empty.")


class NoDefaultSearchColumnError(Exception):
    """Exception raised when a standalone value is found but no default column is set."""

    def __init__(self, value):
        self.value = value
        super().__init__(
            f"Standalone value {value!r} found but no default search column is set."
        )
