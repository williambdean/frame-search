import pytest

import pandas as pd
import narwhals as nw
from frame_search.search import create_search, get_search_parts, SearchPart, parse_query


@pytest.mark.parametrize(
    "query, expected",
    [
        ("bob", [("", "", "bob")]),
        ("name:alice", [("name", "alice", "")]),
        ("age:>30", [("age", ">30", "")]),
        ("age:<30", [("age", "<30", "")]),
        ("age:35.5", [("age", "35.5", "")]),
        ("opening_date:<2023-01-01", [("opening_date", "<2023-01-01", "")]),
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
        (
            'hobby:reading city:"New York"',
            [SearchPart("hobby", ":", "reading"), SearchPart("city", ":", "New York")],
        ),
        ("age:>30", [SearchPart("age", ">", 30)]),
        ("age:>35.6", [SearchPart("age", ">", 35.6)]),
    ],
)
def test_get_search_parts(query, expected) -> None:
    result = get_search_parts(query)
    assert result == expected


@pytest.mark.parametrize(
    "query, idx",
    [
        # ("name:Alice", [0]),
        ("name:alice", [0]),
        # ("bob", [1]),
        # ('hobby:Reading city:"New York"', [0]),
        ('hobby:read city:"New York"', [0]),
        ("age:35", [2]),
        ("age:>30", [2, 3]),
        ("age:<30", [1]),
        ("hobby:Reading age:<30", [1]),
    ],
)
def test_search_functionality(sample_data, search, query, idx) -> None:
    result = nw.from_native(sample_data).filter(search(query)).to_native()
    expected = sample_data.iloc[idx]

    pd.testing.assert_frame_equal(result, expected)
