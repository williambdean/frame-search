"""Tests for parsing search queries."""

import pytest
from frame_search.search import SearchNode, BinaryOp, create_parser


@pytest.mark.parametrize(
    "query",
    [
        "name:alice",
        "name:alice,bob",
        "name:`other_name`",
        "`first name`:alice,bob",
        '`first name`:"alice,bob"',
        "name:1..2",
        "name:alice & last:bob | last:cam",
        "name:alice | last:bob",
        'city:"New York"',
        "age:>30",
        "age:>30.6",
        "`opening date`:>=2023-01-01",
        "~`opening date`:>=2023-01-01",
        "column:==`other column`",
    ],
)
def test_parse_query(query):
    """Test that queries can be parsed without error."""
    parser = create_parser()
    result = parser.parse(query)
    assert result is not None
    # Result should be a SearchNode or BinaryOp
    assert isinstance(result, (SearchNode, BinaryOp))
