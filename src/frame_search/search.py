from .parse import create_parser

from datetime import datetime
from dataclasses import dataclass
from typing import Literal, Optional, Union, TYPE_CHECKING
from lark import Lark, Transformer

if TYPE_CHECKING:
    from lark import Tree

import narwhals as nw


def parse(query: str) -> nw.Expr:
    """Custom parser for search queries from text.

    Parameters
    ----------
    query : str
        The search query string to parse.

    Returns
    -------
    nw.Expr
        A Narwhals expression representing the search query.
        This expression can be used to filter a Narwhals DataFrame.

    Raises
    ------
    EmptySearchQueryError
        If the search query is empty. Empty queries are handled in accessors differently.
    NoDefaultSearchColumnError
        If a standalone value is found in the query but no default search column is set.
    UnknownSearchColumnError
        If a key in the query does not match any column in the schema or mapping.

    """
    parser = create_parser()
    return parser.parse(query)


def search(df, query):
    parser = create_parser()
    node = parser.parse(query)
    return df.filter(node.to_expr())
