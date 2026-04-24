"""Integration tests for search functionality.

These tests verify end-to-end behavior using the search fixture
which is configured via create_search() with column mappings,
default column, and schema.
"""

import pytest

import polars as pl
import polars.testing
import pandas as pd
import narwhals as nw

from frame_search.search import (
    create_search,
    NoDefaultSearchColumnError,
    UnknownSearchColumnError,
    EmptySearchQueryError,
)


# =============================================================================
# Basic Matching Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # Basic string matching
        pytest.param("name:Alice", [0], id="exact-match"),
        pytest.param("name:alice", [0], id="case-insensitive-match"),
        pytest.param("name:ali", [0], id="partial-match-contains"),
        pytest.param("bob", [1], id="default-column-match"),
        pytest.param('city:"New York"', [0, 2], id="quoted-value-with-space"),
        # Multiple conditions (implicit AND - space separated)
        pytest.param(
            'hobby:Reading city:"New York"', [0], id="multiple-conditions-implicit-and"
        ),
        pytest.param(
            'hobby:read city:"New York"',
            [0],
            id="multiple-conditions-case-insensitive",
        ),
        pytest.param(
            "hobby:Reading age:<30", [1], id="multiple-conditions-mixed-types"
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_basic_matching(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Numeric Comparison Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # Exact numeric match
        pytest.param("age:35", [2], id="numeric-exact-match"),
        # Greater than / less than (with colon syntax)
        pytest.param("age:>30", [2, 3], id="numeric-greater-than"),
        pytest.param("age:>=30", [0, 2, 3], id="numeric-greater-than-equal"),
        pytest.param("age:<30", [1], id="numeric-less-than"),
        pytest.param("age:<=30", [0, 1], id="numeric-less-than-equal"),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_numeric_comparisons(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Range Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # Bounded ranges
        pytest.param("age:30..35", [0, 2], id="numeric-range"),
        pytest.param("age:20.0..30", [0, 1], id="numeric-mixed-types-range"),
        pytest.param("first_visit:2022-01-01..2023-12-31", [0, 2], id="date-range"),
        # Unbounded ranges
        pytest.param("age:30..*", [0, 2, 3], id="numeric-range-unbounded-upper"),
        pytest.param("age:*..35", [0, 1, 2], id="numeric-range-unbounded-lower"),
        pytest.param("first_visit:2021-01-01..*", [0, 1, 2], id="date-unbounded-upper"),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_ranges(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Date/Datetime Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        pytest.param("first_visit:<2022-01-01", [1, 3], id="date-less-than"),
        pytest.param(
            "first_visit:>=2022-01-01T12:00:00", [0, 2], id="datetime-comparison"
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_dates(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Multi-value (OR within field) Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        pytest.param("hobby:read,spo", [0, 1, 2], id="multi-value-comma-separated"),
        pytest.param("hobby:Reading,Sports", [0, 1, 2], id="multi-value-full-words"),
        # Regression test for https://github.com/williambdean/frame-search/issues/38
        # Quoted strings with spaces in multi-value (isin) expressions
        pytest.param(
            'city:"New York","Los Angeles"',
            [0, 1, 2],
            id="multi-value-two-quoted-with-spaces",
        ),
        pytest.param(
            'city:"New York","Los Angeles","Charlotte"',
            [0, 1, 2, 3],
            id="multi-value-three-quoted-with-spaces",
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_multi_value(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Negation Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # Dash prefix negation
        pytest.param("-name:Alice", [1, 2, 3], id="negation-dash"),
        pytest.param("-bob", [0, 2, 3], id="negation-dash-default"),
        pytest.param("-age:30..35", [1, 3], id="negation-dash-range"),
        # NOT keyword negation
        pytest.param("NOT name:Alice", [1, 2, 3], id="negation-NOT"),
        pytest.param("NOT bob", [0, 2, 3], id="negation-NOT-default"),
        pytest.param("NOT age:30..35", [1, 3], id="negation-NOT-range"),
        # Tilde negation (new syntax)
        pytest.param("~name:Alice", [1, 2, 3], id="negation-tilde"),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_negation(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Boolean Column Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # is: and has: syntax
        pytest.param("is:older_than_30", [2, 3], id="boolean-is"),
        pytest.param("has:seen_movie", [0, 2], id="boolean-has"),
        # Explicit True/False values
        pytest.param("older_than_30:True", [2, 3], id="boolean-True"),
        pytest.param("older_than_30:False", [0, 1], id="boolean-False"),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_boolean_columns(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Boolean Operators Tests (AND / OR between terms)
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # AND keyword
        pytest.param("name:alice AND age:<=30", [0], id="boolean-AND-keyword"),
        # AND symbol
        pytest.param("name:alice & age:<=30", [0], id="boolean-AND-symbol"),
        # OR keyword
        pytest.param("name:alice OR age:>35", [0, 3], id="boolean-OR-keyword"),
        # OR symbol
        pytest.param("name:alice | age:>35", [0, 3], id="boolean-OR-symbol"),
        # Complex expressions
        pytest.param(
            "(name:alice OR age:>35) AND hobby:reading",
            [0],
            id="complex-parens-and-or",
        ),
        # Precedence: AND binds tighter than OR
        # This should be: name:alice OR (name:bob AND hobby:reading)
        # Alice matches first term, Bob matches second term (Bob + Reading)
        pytest.param(
            "name:alice OR name:bob AND hobby:reading",
            [0, 1],
            id="precedence-and-over-or",
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_boolean_operators(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Parentheses Grouping Tests
# =============================================================================


@pytest.mark.parametrize(
    "query, idx",
    [
        # Simple parentheses (no-op)
        pytest.param("(name:alice)", [0], id="simple-parens"),
        # Parentheses with OR
        pytest.param("(name:alice OR name:bob)", [0, 1], id="parens-or"),
        # Parentheses changing precedence
        pytest.param(
            "(name:alice OR name:bob) AND hobby:reading",
            [0, 1],
            id="parens-or-then-and",
        ),
        # Nested parentheses
        pytest.param(
            "((name:alice OR name:bob) AND hobby:reading) OR name:david",
            [0, 1, 3],
            id="nested-parens",
        ),
        # NOT with parentheses
        pytest.param(
            "NOT (name:alice OR name:bob)",
            [2, 3],
            id="NOT-grouped",
        ),
        pytest.param(
            "~(name:alice OR name:bob)",
            [2, 3],
            id="tilde-grouped",
        ),
        pytest.param(
            "-(name:alice OR name:bob)",
            [2, 3],
            id="dash-grouped",
        ),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_parentheses(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


# =============================================================================
# Error Cases
# =============================================================================


def test_empty_search_raises() -> None:
    search = create_search()
    with pytest.raises(EmptySearchQueryError):
        search("")


def test_search_no_default_raises(sample_data) -> None:
    search = create_search()
    with pytest.raises(NoDefaultSearchColumnError, match="Standalone value"):
        nw.from_native(sample_data).filter(search("alice"))


def test_search_unknown_column_raises(sample_data) -> None:
    search = create_search()
    with pytest.raises(
        UnknownSearchColumnError,
        match="Column 'unknown_column'",
    ):
        nw.from_native(sample_data).filter(search("unknown_column:alice"))
