from .parse import ExprTransformer, Node
from .exceptions import EmptySearchQueryError

from typing import cast

from lark import Lark
import narwhals as nw


def create_parser():
    return Lark.open(
        'grammar.lark', rel_to=__file__, parser='lalr', transformer=ExprTransformer()
    )


def parse(query: str) -> Node:
    """Create a parser.Node that represeents the query

    Parameters
    ----------
    query: str
        The search query string to parse.
    """
    if query.strip() == "":
        raise EmptySearchQueryError()

    parser = create_parser()
    return cast(Node, parser.parse(query))


def search(df, query: str):
    """Custom parser for search queries from text.

    Parameters
    ----------
    df: 
    query: str
        The search query string to parse.

    Returns
    -------
    df

    Raises
    ------
    EmptySearchQueryError
        If the search query is empty. Empty queries are handled in accessors differently.
    """

    expr = parse(query).to_expr()
    return nw.from_native(df).filter(expr).to_native()
