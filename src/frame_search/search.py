from typing import Literal, Optional, Union

from datetime import datetime
from dataclasses import dataclass
import re

import narwhals as nw

Operator = Literal[":", ">", "<"]


def is_date_like(value: str) -> bool:
    """Check if a string is in a date-like format."""
    yyyy_mm_dd_pattern = r"^\d{4}-\d{2}-\d{2}$"

    return re.match(yyyy_mm_dd_pattern, value) is not None


@dataclass
class SearchPart:
    key: Optional[str]
    operator: Optional[Operator]
    value: Union[str, float, int, datetime]

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
            if value.startswith(">") or value.startswith("<"):
                operator = value[0]
                value = value[1:]

            else:
                operator = ":"

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            if is_date_like(value):
                # Convert to date object
                year, month, day = map(int, value.split("-"))
                value = datetime(year, month, day)

            if not isinstance(value, datetime):
                try:
                    value = float(value) if "." in value else int(value)
                except ValueError:
                    pass

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
    NoDefaultSearchColumnError
        If a standalone value is found in the query but no default search column is set.
    UnknownSearchColumnError
        If a key in the query does not match any column in the schema or mapping.

    """

    mapping_to_columns = mapping_to_columns or {}
    schema = schema or nw.Schema()

    def contains(col: str, value: str):
        return nw.col(col).str.to_lowercase().str.contains(value.lower())

    def eq(col: str, value: str):
        return nw.col(col) == value

    def gt(col: str, value: str):
        return nw.col(col) > value

    def lt(col: str, value: str):
        return nw.col(col) < value

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
        elif part.operator == "<":
            expressions.append(lt(col, part.value))
        elif field_dtype == nw.String or isinstance(field_dtype, str):
            expressions.append(contains(col, part.value))
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
