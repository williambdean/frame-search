from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import operator
from typing import Union, Literal, Self, Callable, Protocol, Mapping, Any
from functools import singledispatch

import narwhals as nw

from lark import Transformer, v_args, Token


@dataclass(frozen=True)
class Column:
    name: str | None

    def __call__(self) -> nw.Expr:
        if self.name is None:
            return nw.all()
        return nw.col(self.name)


Value = Union[str, float, int, datetime, bool, None, Column]
Range = namedtuple('Range', ['low', 'high'])
IsIn = namedtuple('IsIn', 'values')


@singledispatch
def comparator(value, col: nw.Expr) -> nw.Expr:
    return col == value

@comparator.register
def _(value: str, col: nw.Expr) -> nw.Expr:
    return col.str.to_lowercase().str.starts_with(value.lower())

@comparator.register
def _(value: IsIn, col: nw.Expr) -> nw.Expr:
    return nw.any_horizontal(
        (col.str.to_lowercase().str.starts_with(str(v).lower()) for v in value.values),
        ignore_nulls=True,
    )

@comparator.register
def _(value: Range, col: nw.Expr) -> nw.Expr:
    return (value.low <= col) & (col <= value.high)

@comparator.register
def _(value: Column, col: nw.Expr) -> nw.Expr:
    return col.is_in(value().unique())


COMPARATORS: Mapping[str, Callable[[nw.Expr, Any], nw.Expr]] = {
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
    ':': lambda left, right: comparator(right, left),
}


class Node(Protocol):
    negated: bool

    def to_expr(self) -> nw.Expr:
        ...

    def replace(self, **kwargs) -> Self:
        return type(self)(**{**vars(self), **kwargs})


@dataclass(frozen=True)
class SearchNode(Node):
    value: Value | IsIn | Range
    comparator: Literal["<", "<=", ">", ">=", "==", "!=", ":"]
    key: Column = Column(None)
    negated: bool = False

    @property
    def is_standalone(self) -> bool:
        """Check if this part is a standalone value without a key."""
        return self.key is None and self.comparator is None

    def to_expr(self) -> nw.Expr:
        func = COMPARATORS[self.comparator]

        if self.negated:
            return ~func(self.key(), self.value, )
        return func(self.key(), self.value)


@dataclass(frozen=True)
class BinaryNode(Node):
    func: Callable[[nw.Expr, nw.Expr], nw.Expr]
    left: Node
    right: Node
    negated: bool = False

    def to_expr(self) -> nw.Expr:
        if self.negated:
            return ~self.func(self.left.to_expr(), self.right.to_expr())
        return self.func(self.left.to_expr(), self.right.to_expr())


@v_args(inline=True)
class ExprTransformer(Transformer):
    def and_(self, left: Node, right: Node) -> BinaryNode:
        return BinaryNode(operator.and_, left, right)

    def or_(self, left: Node, right: Node) -> BinaryNode:
        return BinaryNode(operator.or_, left, right)

    def not_(self, node: Node) -> Node:
        return node.replace(negated=not node.negated)

    def term(self, key: Column, comparator: Literal["<", "<=", ">", ">=", "==", "!=", ":"], value: Value) -> SearchNode:
        return SearchNode(value=value, comparator=comparator, key=key)

    def key(self, token: Token) -> Column:
        if token.type == 'BACKTICKED_KEY':
            return Column(token.value[1:-1])
        elif token.type == 'WORD':
            return Column(token.value)
        msg = f"Unexpected 'key' token: {token!r}"
        raise ValueError(msg)

    def value(self, token: Token) -> Value:
        if token.type in ['DATE', 'DATETIME']:
            return datetime.fromisoformat(token.value)
        elif token.type == 'WORD':
            return str(token.value)
        elif token.type == 'ESCAPED_STRING':
            return str(token.value[1:-1])
        elif token.type == 'INT':
            return int(token.value)
        elif token.type == 'FLOAT':
            return float(token.value)
        elif token.type == 'BOOL':
            if token.value == 'True':
                return True
            elif token.value == 'False':
                return False
            msg = "Lexer specified a BOOL, but parser does not know how to handle it"
            raise ValueError(msg)
        elif token.type == 'BACKTICKED_KEY':
            return Column(token.value[1:-1])
        msg = f"Unexpected 'value' token: {token!r}"
        raise ValueError(msg)


    @v_args()
    def isin(self, values: list[Value]) -> IsIn:
        return IsIn(values)

    def range(self, low: Value, high: Value) -> Range:
        return Range(low=low, high=high)

