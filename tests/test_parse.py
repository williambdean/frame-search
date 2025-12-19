from datetime import datetime
import operator

from frame_search.parse import SearchNode, BinaryNode, Column, IsIn, Range
from frame_search import parse
import pytest
from frame_search.exceptions import EmptySearchQueryError


@pytest.mark.parametrize(
    "query, expected",
    [
        ("name:alice", SearchNode("alice", key=Column("name"), comparator=":")),
        ("name==alice", SearchNode("alice", key=Column("name"), comparator="==")),
        ("name:alice,bob", SearchNode(IsIn(["alice", "bob"]), key=Column("name"), comparator=":")),
        ("name==alice,bob", SearchNode(IsIn(["alice", "bob"]), key=Column("name"), comparator="==")),
        ("name==`other_name`", SearchNode(Column("other_name"), key=Column("name"), comparator="==")),
        ("`first name`:alice,bob", SearchNode(IsIn(["alice", "bob"]), key=Column("first name"), comparator=":")),
        ('`first name`:"alice,bob"', SearchNode("alice,bob", key=Column("first name"), comparator=":")),
        ('`first name`:"alice","bob"', SearchNode(IsIn(["alice", "bob"]), key=Column("first name"), comparator=":")),
        ("name:1..2", SearchNode(Range(1, 2), key=Column("name"), comparator=":")),
        ("name:alice & last:bob | last:charlie", BinaryNode(
                operator.or_,
                BinaryNode(
                    operator.and_,
                    SearchNode("alice", key=Column("name"), comparator=":"),
                    SearchNode("bob", key=Column("last"), comparator=":"),
                ),
                SearchNode("charlie", key=Column("last"), comparator=":")
            )
        ),
        ("name:alice | last:bob", BinaryNode(
                operator.or_,
                SearchNode("alice", key=Column("name"), comparator=":"),
                SearchNode("bob", key=Column("last"), comparator=":"),
            )
        ),
        ('city:"New York"', SearchNode("New York", key=Column("city"), comparator=":")),
        ('age<30', SearchNode(30, comparator="<", key=Column("age"))),
        ('age<30.6', SearchNode(30.6, comparator="<", key=Column("age"))),
        ('`opening date`>=2023-01-01', SearchNode(datetime(2023, 1, 1), comparator=">=", key=Column("opening date"))),
        ('`opening date`>=2023-01-01', SearchNode(datetime(2023, 1, 1), comparator=">=", key=Column("opening date"))),
        ('~`opening date`>=2023-01-01', SearchNode(datetime(2023, 1, 1), comparator=">=", key=Column("opening date"), negated=True)),
        ('`someone\'s column`>=2023-01-01', SearchNode(datetime(2023, 1, 1), comparator=">=", key=Column("someone's column"))),
        ('column==`other column`', SearchNode(Column("other column"), comparator="==", key=Column("column"))),
    ]
)
def test_smoke_parser(query, expected) -> None:
    assert parse(query) == expected


def test_empty_parse() -> None:
    with pytest.raises(EmptySearchQueryError):
        parse("")
