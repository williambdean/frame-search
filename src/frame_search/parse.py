from collections import namedtuple, defaultdict
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum, auto
from itertools import pairwise
import operator
from typing import Union, Optional, Literal, Self, Callable

import narwhals as nw

from lark import Lark, Transformer, v_args, Token
import operator

@dataclass
class Column:
    name: str

    def __call__(self):
        return nw.col(self.name)

Value = Union[str, float, int, datetime, None, nw.Expr]


Range = namedtuple('Range', ['low', 'high'])
IsIn = namedtuple('IsIn', 'values')


COMPARATORS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.ge,
    ">=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

VALUE_DEPENDENT_COMPARATORS = defaultdict(
    lambda: operator.eq,
    {
        str: lambda col, value: col.str.contains(value),
        list: lambda col, value: col.is_in(value),
        IsIn: lambda col, value: col.is_in(value.values),
        Range: lambda col, value: value.low <= col <= value.high,
        Column: lambda col, value: col.is_in(value.unique()),
    }
)


def create_parser():
    return Lark.open('grammar.lark', rel_to=__file__, parser='lalr', transformer=ExprTransformer())


from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def to_expr(self): pass

@dataclass
class SearchNode(Node):
    value: Value | IsIn | Range
    key: Optional[nw.Expr] = None
    comparator: Literal[*COMPARATORS] | None = None
    negated: bool = False

    @property
    def is_standalone(self) -> bool:
        """Check if this part is a standalone value without a key."""
        return self.key is None and self.comparator is None

    def to_expr(self):
        key = nw.all() if self.key is None else self.key

        if self.comparator is None:
            func = VALUE_DEPENDENT_COMPARATORS[type(self.value)]
        else:
            func = COMPARATORS[self.comparator]

        if self.negated:
            return ~func(key, self.value)
        return func(key, self.value)

@dataclass
class BinaryOp(Node):
    func: Callable[[Node, Node], [Node]]
    left: Node
    right: Node

    def to_expr(self):
        return self.func(self.left.to_expr(), self.right.to_expr())


@v_args(inline=True)
class ExprTransformer(Transformer):
    def and_(self, left: nw.Expr, right: nw.Expr) -> BinaryOp:
        return BinaryOp(operator.and_, left, right)

    def or_(self, left: Node, right: Node) -> BinaryOp:
        return BinaryOp(operator.or_, left, right)

    def not_(self, node: SearchNode):
        return replace(node, negated=not node.negated)

    @v_args()
    def term(self, parts: list[Value]) -> nw.Expr:
        key = comparator = value = None
        match parts:
            case (value, ): pass
            case (key, value): pass
            case (key, comparator, value): pass

        return SearchNode(value=value, comparator=comparator, key=key)

    def value(self, token: Token) -> Value:
        return maybe_parse(token.value)

    @v_args()
    def isin(self, values: list[Value]) -> IsIn:
        return IsIn(values)

    def range(self, low: Value, high: Value) -> Range:
        return Range(low=low, high=high)

    def COMPARATOR(self, token: Token) -> str:
        return token.value

    def BACKTICKED_KEY(self, token: Token) -> nw.Expr:
        return Column(token.value[1:-1])

    def BARE_KEY(self, token: Token) -> nw.Expr:
        return Column(token.value)

    def ESCAPED_STRING(self, token: Token) -> Token:
        return token.update(value=token.value[1:-1])


def maybe_parse(value: str) -> Value:
    match value.casefold():
        case 'nan': return float('nan')
        case 'none' | 'null': return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        pass

    return value

