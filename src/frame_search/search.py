"""Search query parsing and execution.

This module provides the main API for parsing search queries and filtering DataFrames.
"""

from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Callable, Optional, Union
import operator

import narwhals as nw
from lark import Lark, Transformer, v_args, Token

from .exceptions import (
    EmptySearchQueryError,
    NoDefaultSearchColumnError,
    UnknownSearchColumnError,
)

# Re-export exceptions for backward compatibility
__all__ = [
    "parse",
    "search",
    "create_search",
    "parse_search_query",
    "EmptySearchQueryError",
    "NoDefaultSearchColumnError",
    "UnknownSearchColumnError",
]


# =============================================================================
# Value Types
# =============================================================================

Value = Union[str, float, int, datetime, bool, None]

Range = namedtuple("Range", ["low", "high"])
IsIn = namedtuple("IsIn", "values")


# =============================================================================
# Comparators
# =============================================================================

COMPARATORS: dict[str, Callable] = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


# =============================================================================
# AST Nodes
# =============================================================================


@dataclass
class SearchNode:
    """A search term node (key:value, is:column, has:column, no:column, or standalone value)."""

    value: Value | IsIn | Range
    key: Optional[str] = None
    comparator: Optional[str] = None
    negated: bool = False
    is_boolean_column: bool = False  # For is: syntax
    is_null_check: bool = False  # For has: (not null) and no: (is null) syntax

    @property
    def is_standalone(self) -> bool:
        """Check if this is a standalone value without a key."""
        return (
            self.key is None
            and self.comparator is None
            and not self.is_boolean_column
            and not self.is_null_check
        )


@dataclass
class BinaryOp:
    """Binary operator node (AND/OR)."""

    func: Callable
    left: "SearchNode | BinaryOp"
    right: "SearchNode | BinaryOp"


Node = Union[SearchNode, BinaryOp]


# =============================================================================
# Value Parsing
# =============================================================================


def maybe_parse(value: str) -> Value:
    """Parse a string value into the appropriate type."""
    lowered = value.casefold()
    if lowered == "nan":
        return float("nan")
    elif lowered in ("none", "null"):
        return None
    elif lowered == "true":
        return True
    elif lowered == "false":
        return False

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        pass

    return value


# =============================================================================
# Lark Transformer
# =============================================================================


def create_parser():
    """Create a Lark parser for search queries."""
    return Lark.open(
        "grammar.lark", rel_to=__file__, parser="lalr", transformer=ExprTransformer()
    )


@v_args(inline=True)
class ExprTransformer(Transformer):
    """Transform parse tree into AST nodes."""

    def and_(self, left: Node, right: Node) -> BinaryOp:
        return BinaryOp(operator.and_, left, right)

    def or_(self, left: Node, right: Node) -> BinaryOp:
        return BinaryOp(operator.or_, left, right)

    def not_(self, node: Node) -> Node:
        if isinstance(node, SearchNode):
            return replace(node, negated=not node.negated)
        elif isinstance(node, BinaryOp):
            # Apply De Morgan's law: NOT (A AND B) = (NOT A) OR (NOT B)
            # NOT (A OR B) = (NOT A) AND (NOT B)
            negated_left = self.not_(node.left)
            negated_right = self.not_(node.right)
            if node.func == operator.and_:
                return BinaryOp(operator.or_, negated_left, negated_right)
            else:
                return BinaryOp(operator.and_, negated_left, negated_right)
        return node

    def boolean_column(self, prefix: Token, column: Token) -> SearchNode:
        """Handle is:column syntax — column value is True."""
        return SearchNode(
            key=column.value,
            value=True,
            is_boolean_column=True,
        )

    def null_check(self, prefix: Token, column: Token) -> SearchNode:
        """Handle has:column (not null) and no:column (is null) syntax."""
        is_null = prefix.value.lower().startswith("no")
        return SearchNode(
            key=column.value,
            value=None,
            is_null_check=True,
            negated=is_null,  # negated=True means "is null" (no:), False means "not null" (has:)
        )

    def key_value(self, *parts) -> SearchNode:
        """Handle key:comparator?value syntax."""
        key = comparator = value = None
        if len(parts) == 2:
            key, value = parts
        elif len(parts) == 3:
            key, comparator, value = parts
        return SearchNode(key=key, value=value, comparator=comparator)

    def standalone(self, token: Token) -> SearchNode:
        """Handle standalone values without a key."""
        return SearchNode(value=maybe_parse(token.value))

    def value(self, token: Token) -> Value:
        return maybe_parse(token.value)

    @v_args()
    def isin(self, values: list[Value]) -> IsIn:
        return IsIn(values)

    def range(self, low: Value, high: Value) -> Range:
        # Handle wildcard ranges
        if low == "*":
            low = None
        if high == "*":
            high = None
        return Range(low=low, high=high)

    def COMPARATOR(self, token: Token) -> str:
        return token.value

    def WILDCARD(self, token: Token) -> str:
        return "*"

    def KEY_COLON(self, token: Token) -> str:
        """Handle KEY_COLON terminal - strip the trailing colon."""
        key = token.value[:-1]  # Remove trailing colon
        # Handle backticked keys
        if key.startswith("`") and key.endswith("`"):
            return key[1:-1]
        return key

    def BACKTICKED_KEY(self, token: Token) -> str:
        return token.value[1:-1]

    def ESCAPED_STRING(self, token: Token) -> Token:
        return token.update(value=token.value[1:-1])


# =============================================================================
# Expression Building
# =============================================================================


def _resolve_column(
    key: str,
    mapping_to_columns: dict[str, str],
    schema: nw.Schema,
) -> str:
    """Resolve a search key to a column name."""
    # Check mapping first
    if key in mapping_to_columns:
        return mapping_to_columns[key]

    # Check schema (case-insensitive)
    for schema_col in schema.keys():
        if key.lower() == schema_col.lower():
            return schema_col

    raise UnknownSearchColumnError(key)


def _build_expr(
    node: Node,
    mapping_to_columns: dict[str, str],
    default: Optional[str],
    schema: nw.Schema,
) -> nw.Expr:
    """Build a narwhals expression from an AST node."""
    if isinstance(node, BinaryOp):
        left_expr = _build_expr(node.left, mapping_to_columns, default, schema)
        right_expr = _build_expr(node.right, mapping_to_columns, default, schema)
        return node.func(left_expr, right_expr)

    # It's a SearchNode
    search_node: SearchNode = node  # type: ignore[assignment]

    # Resolve column
    if search_node.is_boolean_column:
        assert search_node.key is not None
        col = _resolve_column(search_node.key, mapping_to_columns, schema)
        expr = nw.col(col)
        if search_node.negated:
            expr = ~expr
        return expr

    if search_node.is_null_check:
        assert search_node.key is not None
        col = _resolve_column(search_node.key, mapping_to_columns, schema)
        if search_node.negated:  # no:col — is null
            return nw.col(col).is_null()
        else:  # has:col — is not null
            return ~nw.col(col).is_null()

    if search_node.is_standalone:
        if default is None:
            raise NoDefaultSearchColumnError(search_node.value)
        col = default
    else:
        assert search_node.key is not None
        col = _resolve_column(search_node.key, mapping_to_columns, schema)

    field_dtype = schema.get(col, nw.String)
    value = search_node.value

    # Handle unbounded ranges by converting to comparisons
    if isinstance(value, Range):
        if value.low is None and value.high is not None:
            # *..high => col <= high
            expr = nw.col(col) <= value.high
        elif value.low is not None and value.high is None:
            # low..* => col >= low
            expr = nw.col(col) >= value.low
        else:
            # low..high => low <= col <= high
            expr = (nw.col(col) >= value.low) & (nw.col(col) <= value.high)
    elif search_node.comparator is not None:
        # Explicit comparator
        cmp_func = COMPARATORS[search_node.comparator]
        expr = cmp_func(nw.col(col), value)
    elif isinstance(value, IsIn):
        # Multi-value OR within field: hobby:read,spo
        if field_dtype == nw.String or isinstance(field_dtype, str):
            # For strings, do case-insensitive contains for each value
            exprs = [
                nw.col(col).str.to_lowercase().str.contains(v.lower())
                for v in value.values
                if isinstance(v, str)
            ]
            expr = exprs[0]
            for e in exprs[1:]:
                expr = expr | e
        else:
            expr = nw.col(col).is_in(list(value.values))
    elif field_dtype == nw.String or isinstance(field_dtype, str):
        # String column: case-insensitive contains
        if isinstance(value, str):
            expr = nw.col(col).str.to_lowercase().str.contains(value.lower())
        else:
            expr = nw.col(col) == value
    else:
        # Numeric/other: equality
        expr = nw.col(col) == value

    if search_node.negated:
        expr = ~expr

    return expr


# =============================================================================
# Public API
# =============================================================================


def parse_search_query(
    query: str,
    mapping_to_columns: Optional[dict[str, str]] = None,
    default: Optional[str] = None,
    schema: Optional[nw.Schema] = None,
) -> nw.Expr:
    """Parse a search query string into a narwhals expression.

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

    Raises
    ------
    EmptySearchQueryError
        If the search query is empty.
    NoDefaultSearchColumnError
        If a standalone value is found in the query but no default search column is set.
    UnknownSearchColumnError
        If a key in the query does not match any column in the schema or mapping.
    """
    if not query.strip():
        raise EmptySearchQueryError()

    mapping_to_columns = mapping_to_columns or {}
    schema = schema or nw.Schema()

    parser = create_parser()
    ast: Node = parser.parse(query)  # type: ignore[assignment]

    return _build_expr(ast, mapping_to_columns, default, schema)


def create_search(
    mapping_to_columns: Optional[dict[str, str]] = None,
    default: Optional[str] = None,
    schema: Optional[nw.Schema] = None,
) -> Callable[[str], nw.Expr]:
    """Create a configured search function.

    Parameters
    ----------
    mapping_to_columns : dict[str, str] | None, optional
        A mapping from search keys to column names.
    default : str | None, optional
        The default column to search in if no key is provided.
    schema : nw.Schema | None, optional
        The schema of the dataset to search against.

    Returns
    -------
    Callable[[str], nw.Expr]
        A function that takes a query string and returns a narwhals expression.
    """

    def search_fn(query: str) -> nw.Expr:
        return parse_search_query(
            query=query,
            mapping_to_columns=mapping_to_columns,
            default=default,
            schema=schema,
        )

    return search_fn


def parse(query: str) -> nw.Expr:
    """Parse a search query string (no configuration).

    This is a simple wrapper for basic usage without column mapping or schema.
    For more control, use `create_search()` or `parse_search_query()`.
    """
    return parse_search_query(query)


def search(df, query: str):
    """Filter a DataFrame using a search query.

    This is a simple wrapper for basic usage. For more control,
    use `create_search()` to create a configured search function.
    """
    expr = parse_search_query(query)
    return df.filter(expr)
