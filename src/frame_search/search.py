from typing import Literal, Optional, Union

from datetime import datetime
from dataclasses import dataclass
import re

import narwhals as nw

Operator = Literal[":", ">", "<", ">=", "<="]

Value = Union[str, float, int, datetime]


@dataclass
class Range:
    lower: Value
    upper: Value

    def __post_init__(self):
        if type(self.lower) is not type(self.upper):
            raise TypeError(
                f"Lower and upper bounds must be of the same type: {type(self.lower)} vs {type(self.upper)}"
            )


def is_date_like(value: str) -> bool:
    """Check if a string is in a date-like format."""
    # Updated regex to support more comprehensive date and datetime formats
    # Supports YYYY-MM-DD and ISO 8601 formats like YYYY-MM-DDTHH:MM:SS
    # For more details on ISO 8601, see: https://www.iso.org/iso-8601-date-and-time-format.html
    # Regex allows for optional time, timezone, and fractional seconds
    iso_8601_pattern = (
        r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
    )
    return re.match(iso_8601_pattern, value) is not None


@dataclass
class SearchPart:
    key: Optional[str]
    operator: Optional[Operator]
    value: Union[Value, Range]

    @property
    def is_standalone(self) -> bool:
        """Check if this part is a standalone value without a key."""
        return self.key is None and self.operator is None


def parse_query(query: str):
    # Regex to capture:
    # 1. key:operator:value (e.g., name:alice, age:">30", city:"New York")
    #    - Group 1: key (\w+)
    #    - Group 2: operator (:|>|<)
    #    - Group 3: value (either "[^"]*" for quoted strings or \S+ for non-whitespace)
    # 2. standalone value (\S+)
    #    - Group 4: standalone value
    pattern = r'(\w+):("[^"]*"|\S+)|(\S+)'
    return list(re.findall(pattern, query))


def _parse_value(value: str) -> Value:
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    if is_date_like(value):
        try:
            # Handle ISO 8601 format, replacing 'Z' with timezone offset for compatibility
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value)
        except ValueError:
            # Fallback for simple date format YYYY-MM-DD
            year, month, day = map(int, value.split("-"))
            return datetime(year, month, day)

    if not isinstance(value, datetime):
        try:
            value = float(value) if "." in value else int(value)
        except ValueError:
            pass

    return value


def _make_same_type(
    first: Value,
    second: Value,
) -> tuple[Value, Value]:
    """Ensure both values are of the same type."""

    if isinstance(first, float) or isinstance(second, float):
        first, second = float(first), float(second)

    return first, second


def get_search_parts(query: str) -> list[SearchPart]:
    """Parse a search query string into a list of SearchPart objects."""
    matches = parse_query(query)

    search_parts = []
    for match in matches:
        if match[2]:  # This is the standalone value group
            value = match[2]
            search_parts.append(SearchPart(key=None, operator=None, value=value))
        else:  # This is the key:operator:value group
            key = match[0]
            value = match[1]
            if value.startswith(">=") or value.startswith("<="):
                operator = value[:2]
                value = value[2:]
            elif value.startswith(">") or value.startswith("<"):
                operator = value[0]
                value = value[1:]

            else:
                operator = ":"

            if ".." in value:
                values = value.split("..")
                if len(values) != 2:
                    raise ValueError(f"Invalid range format in value: {value}")

                lower, upper = map(_parse_value, values)
                lower = None if lower == "*" else lower
                upper = None if upper == "*" else upper

                if lower is None:
                    operator = "<="
                    value = upper
                elif upper is None:
                    operator = ">="
                    value = lower
                else:
                    operator = ":"
                    lower, upper = _make_same_type(lower, upper)
                    value = Range(lower=lower, upper=upper)

                search_parts.append(SearchPart(key=key, operator=operator, value=value))

            else:
                value = _parse_value(value)
                search_parts.append(SearchPart(key=key, operator=operator, value=value))

    return search_parts


class NoDefaultSearchColumnError(Exception):
    """Exception raised when no default search column is set."""

    def __init__(self, value):
        self.value = value

        super().__init__(
            f"Standalone value {value!r} found but no default search column is set."
        )


class UnknownSearchColumnError(Exception):
    """Exception raised when an unknown search column is referenced."""

    def __init__(self, key):
        self.key = key
        super().__init__(f"Column {key!r} not found in schema or mapping.")


class EmptySearchQueryError(Exception):
    """Exception raised when an empty search query is provided."""

    def __init__(self):
        super().__init__("Search query cannot be empty.")


def parse_search_query(
    query: str,
    mapping_to_columns: Optional[dict[str, str]] = None,
    default: Optional[str] = None,
    schema: Optional[nw.Schema] = None,
) -> nw.Expr:
    """Custom parser for search queries from text.

    Parameters
    ----------
    query : str
        The search query string to parse.
    mapping_to_columns : dict[str, str] | None, optional
        A mapping from search keys to column names. If None, the keys will be matched
        directly to the schema columns.
    default : str | None, optional
        The default column to search in if no key is provided in the query.
        If None, an error will be raised if a standalone value is found without a key.
    schema : nw.Schema | None, optional
        The schema of the dataset to search against. If None, an empty schema is used.

    Returns
    -------
    nw.Expr
        A Narwhals expression representing the search query.
        This expression can be used to filter a Narwhals DataFrame.

    Raises
    ------
    EmptySearchQueryError
        If the search query is empty. Empty queries are handled in accessors differently.
    NoDefaultSearchColumnError
        If a standalone value is found in the query but no default search column is set.
    UnknownSearchColumnError
        If a key in the query does not match any column in the schema or mapping.

    """
    if not query.strip():
        raise EmptySearchQueryError()

    mapping_to_columns = mapping_to_columns or {}
    schema = schema or nw.Schema()

    def contains(col: str, value: str):
        return (
            nw.col(col).str.to_lowercase().str.contains(value.lower().replace(",", "|"))
        )

    def eq(col: str, value: str):
        return nw.col(col) == value

    def gt(col: str, value: str):
        return nw.col(col) > value

    def ge(col: str, value: str):
        return nw.col(col) >= value

    def lt(col: str, value: str):
        return nw.col(col) < value

    def le(col: str, value: str):
        return nw.col(col) <= value

    parts = get_search_parts(query)

    expressions = []
    for part in parts:
        if part.is_standalone:
            if default is not None and isinstance(part.value, str):
                expressions.append(contains(default, part.value))
            else:
                raise NoDefaultSearchColumnError(part.value)
            continue

        col = None
        if part.key:
            if part.key in mapping_to_columns:
                col = mapping_to_columns[part.key]
            else:
                for schema_col in schema.keys():
                    if part.key.lower() == schema_col.lower():
                        col = schema_col
            if col is None:
                raise UnknownSearchColumnError(part.key)
        elif default is not None:
            col = default
        else:
            raise NoDefaultSearchColumnError(part.value)

        field_dtype = schema.get(col, nw.String)

        if part.operator == ">":
            expressions.append(gt(col, part.value))
        elif part.operator == ">=":
            expressions.append(ge(col, part.value))
        elif part.operator == "<":
            expressions.append(lt(col, part.value))
        elif part.operator == "<=":
            expressions.append(le(col, part.value))
        elif field_dtype == nw.String or isinstance(field_dtype, str):
            expressions.append(contains(col, part.value))
        elif isinstance(part.value, Range):
            expressions.append(ge(col, part.value.lower) & le(col, part.value.upper))
        else:
            expressions.append(eq(col, part.value))

    # Combine all expressions with an AND
    if not expressions:
        return nw.lit(True)

    combined_expression = expressions[0]
    for expr in expressions[1:]:
        combined_expression = combined_expression & expr

    return combined_expression


def create_search(
    mapping_to_columns: Optional[dict[str, str]] = None,
    default: Optional[str] = None,
    schema: Optional[nw.Schema] = None,
):
    """Create a search expression with the given default and mapping."""

    def search(query: str) -> nw.Expr:
        return parse_search_query(
            query=query,
            mapping_to_columns=mapping_to_columns,
            default=default,
            schema=schema,
        )

    return search
