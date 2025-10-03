from pprint import pprint
from frame_search.parse import SearchNode, BinaryOp
from frame_search.search import parse

tests = [
    "name:alice",
    "name:alice,bob",
    "name:`other_name`",
    '`first name`:alice,bob',
    '`first name`:"alice,bob"',
    "name:1..2",
    "name:alice & last:bob | last:cam",
    "name:alice | last:bob",
    'city:"New York"',
    "age:>30",
    "age:>30.6",
    '`opening date`:>=2023-01-01',
    '`opening date`:>=2023-01-01',
    '~`opening date`:>=2023-01-01',
    r'`someone\'s column`:>=2023-01-01',
    'column:==`other column`',
]

for query in tests:
    print(f"{query = }")
    pprint(parse(query))
    print()

