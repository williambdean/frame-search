import pytest

from datetime import datetime

import polars as pl
import polars.testing
import pandas as pd
import narwhals as nw

from frame_search.search import (
    get_search_parts,
    SearchPart,
    parse_query,
    create_search,
    NoDefaultSearchColumnError,
    UnknownSearchColumnError,
    EmptySearchQueryError,
    Range,
)


@pytest.mark.parametrize(
    "lower, upper",
    [
        (1, 10.0),
        (datetime(2023, 1, 1), 1),
        (datetime(2023, 1, 1), 1.0),
    ],
)
def test_range_different_type_raises(lower, upper) -> None:
    with pytest.raises(
        TypeError,
        match="Lower and upper bounds must be of the same type",
    ):
        Range(lower, upper)


@pytest.mark.parametrize(
    "query, expected",
    [
        pytest.param("", [], id="empty-query"),
        pytest.param("bob", [("", "", "bob")], id="default"),
        pytest.param("name:alice", [("name", "alice", "")], id="contains-match"),
        pytest.param("age:>=30", [("age", ">=30", "")], id="ge"),
        pytest.param("age:>30", [("age", ">30", "")], id="gt"),
        pytest.param("age:<30", [("age", "<30", "")], id="lt"),
        pytest.param("age:35.5", [("age", "35.5", "")], id="exact-numeric"),
        pytest.param(
            "opening_date:<2023-01-01",
            [("opening_date", "<2023-01-01", "")],
            id="date-lt",
        ),
        pytest.param("bob age:>30", [("", "", "bob"), ("age", ">30", "")], id="mixed"),
        pytest.param(
            'hobby:reading city:"New York"',
            [
                ("hobby", "reading", ""),
                ("city", '"New York"', ""),
            ],
            id="multiple-conditions",
        ),
    ],
)
def test_parse_query(query, expected) -> None:
    result = parse_query(query)
    assert result == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        ("bob", [SearchPart(None, None, "bob")]),
        ("name:alice", [SearchPart("name", ":", "alice")]),
        ("age:>=30", [SearchPart("age", ">=", 30)]),
        (
            'hobby:reading city:"New York"',
            [SearchPart("hobby", ":", "reading"), SearchPart("city", ":", "New York")],
        ),
        ("age:>30", [SearchPart("age", ">", 30)]),
        ("age:>35.6", [SearchPart("age", ">", 35.6)]),
        (
            "opening_date:>2023-01-01",
            [SearchPart("opening_date", ">", datetime(2023, 1, 1))],
        ),
    ],
)
def test_get_search_parts(query, expected) -> None:
    result = get_search_parts(query)
    assert result == expected


@pytest.mark.parametrize(
    "query, idx",
    [
        pytest.param("name:Alice", [0], id="exact-match"),
        pytest.param("name:alice", [0], id="case-insensitive-match"),
        pytest.param("bob", [1], id="default-column-match"),
        pytest.param('hobby:Reading city:"New York"', [0], id="multiple-conditions"),
        pytest.param(
            'hobby:read city:"New York"',
            [0],
            id="multiple-conditions-case-insensitive",
        ),
        pytest.param("age:35", [2], id="numeric-exact-match"),
        pytest.param("age:>30", [2, 3], id="numeric-greater-than"),
        pytest.param("age:30..35", [0, 2], id="numeric-range"),
        pytest.param("age:30..*", [0, 2, 3], id="numeric-range-unbounded-upper"),
        pytest.param("age:>=30", [0, 2, 3], id="numeric-greater-than-equal"),
        pytest.param("age:*..35", [0, 1, 2], id="numeric-range-unbounded-lower"),
        pytest.param("age:<30", [1], id="numeric-less-than"),
        pytest.param("age:<=30", [0, 1], id="numeric-less-than-equal"),
        pytest.param("age:20.0..30", [0, 1], id="numeric-mixed-types-range"),
        pytest.param("hobby:Reading age:<30", [1], id="multiple-conditions-mixed"),
        pytest.param("first_visit:<2022-01-01", [1, 3], id="date"),
        pytest.param("first_visit:2022-01-01..2023-12-31", [0, 2], id="date-range"),
        pytest.param("first_visit:2021-01-01..*", [0, 1, 2], id="date-unbounded-upper"),
        pytest.param(
            "hobby:read|spo",
            [0, 1, 2],
            id="logical-or-pipe-separated",
        ),
        pytest.param("hobby:read,spo", [0, 1, 2], id="logical-or-comma-separated"),
        pytest.param(
            "hobby:Reading,Sports", [0, 1, 2], id="logical-or-comma-separator"
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
def test_search_functionality(request, fixture_name, search, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = nw.from_native(data).filter(search(query)).to_native()
    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)


def test_empty_search() -> None:
    search = create_search()
    with pytest.raises(EmptySearchQueryError):
        search("")


def test_search_no_default(sample_data) -> None:
    search = create_search()
    with pytest.raises(NoDefaultSearchColumnError, match="Standalone value"):
        nw.from_native(sample_data).filter(search("alice"))


def test_search_unknown_column(sample_data) -> None:
    search = create_search()
    with pytest.raises(
        UnknownSearchColumnError,
        match="Column 'unknown_column'",
    ):
        nw.from_native(sample_data).filter(search("unknown_column:alice"))
