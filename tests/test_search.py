import pytest

from datetime import datetime

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
        ("", []),
        ("bob", [("", "", "bob")]),
        ("name:alice", [("name", "alice", "")]),
        ("age:>=30", [("age", ">=30", "")]),
        ("age:>30", [("age", ">30", "")]),
        ("age:<30", [("age", "<30", "")]),
        ("age:35.5", [("age", "35.5", "")]),
        ("opening_date:<2023-01-01", [("opening_date", "<2023-01-01", "")]),
        ("bob age:>30", [("", "", "bob"), ("age", ">30", "")]),
        (
            'hobby:reading city:"New York"',
            [
                ("hobby", "reading", ""),
                ("city", '"New York"', ""),
            ],
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
        ("name:Alice", [0]),
        ("name:alice", [0]),
        ("bob", [1]),
        ('hobby:Reading city:"New York"', [0]),
        ('hobby:read city:"New York"', [0]),
        ("age:35", [2]),
        ("age:>30", [2, 3]),
        ("age:30..35", [0, 2]),
        ("age:30..*", [0, 2, 3]),
        ("age:>=30", [0, 2, 3]),
        ("age:*..35", [0, 1, 2]),
        ("age:<30", [1]),
        ("age:<=30", [0, 1]),
        ("age:20.0..30", [0, 1]),
        ("hobby:Reading age:<30", [1]),
        ("first_visit:<2022-01-01", [1, 3]),
        ("first_visit:2022-01-01..2023-12-31", [0, 2]),
        ("first_visit:2021-01-01..*", [0, 1, 2]),
    ],
)
def test_search_functionality(sample_data, search, query, idx) -> None:
    result = nw.from_native(sample_data).filter(search(query)).to_native()
    expected = sample_data.iloc[idx]

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
