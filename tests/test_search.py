import pytest

import polars as pl
import polars.testing
import pandas as pd

from frame_search import search
from frame_search.parse import Range


@pytest.mark.parametrize(
    "query, idx",
    [
        pytest.param("Name:Alic", [0], id="prefix-match"),
        pytest.param("Name:alic", [0], id="case-insensitive-match"),
        pytest.param('Hobby:Reading & `City of Interest`:"New York"', [0], id="multiple-conditions-amp"),
        pytest.param('Hobby:Reading AND `City of Interest`:"New York"', [0], id="multiple-conditions-and"),
        pytest.param('Hobby:Reading | `City of Interest`:"New York"', [0, 1, 2], id="multiple-conditions-vpipe"),
        pytest.param('Hobby:Reading OR `City of Interest`:"New York"', [0, 1, 2], id="multiple-conditions-or"),
        pytest.param(
            'Hobby:read & `City of Interest`:"New York"',
            [0],
            id="multiple-conditions-case-insensitive",
        ),
        pytest.param("Age==35", [2], id="numeric-exact-match"),
        pytest.param("Age>30", [2, 3], id="numeric-greater-than"),
        pytest.param("Age:30..35", [0, 2], id="numeric-range"),
        pytest.param("Age>=30", [0, 2, 3], id="numeric-greater-than-equal"),
        pytest.param("Age<30", [1], id="numeric-less-than"),
        pytest.param("Age<=30", [0, 1], id="numeric-less-than-equal"),
        pytest.param("Age:20.0..30", [0, 1], id="numeric-mixed-types-range"),
        pytest.param("Hobby:Reading & Age<30", [1], id="multiple-conditions-mixed"),
        pytest.param("`First Visit`<2022-01-01", [1, 3], id="date"),
        pytest.param("`First Visit`:2022-01-01..2023-12-31", [0, 2], id="date-range"),
        pytest.param(
            "Hobby:read,spo",
            [0, 1, 2],
            id="logical-or-pipe-separated",
        ),
        pytest.param("Hobby:read,spo", [0, 1, 2], id="logical-or-comma-separated"),
        pytest.param(
            "Hobby:Reading,Sports", [0, 1, 2], id="logical-or-comma-separator"
        ),
        pytest.param("`First Visit`>=2022-01-01T12:00:00", [0, 2], id="datetime"),
        pytest.param("~Name:Alice", [1, 2, 3], id="negation-tilde"),
        pytest.param("NOT Name:Alice", [1, 2, 3], id="negation-NOT"),
        pytest.param('~(Hobby:Reading AND `City of Interest`:"New York")', [1, 2, 3], id="negation-multiple-conditions-and"),
        pytest.param('~(Hobby:Reading OR `City of Interest`:"New York")', [3], id="negation-multiple-conditions-or"),
        pytest.param("older_than_30:True", [2, 3], id="boolean-True"),
        pytest.param("older_than_30:False", [0, 1], id="boolean-False"),
    ],
)
@pytest.mark.parametrize(
    "fixture_name",
    [
        pytest.param("sample_data", id="pandas"),
        pytest.param("sample_data_polars", id="polars"),
    ],
)
def test_search_functionality(request, fixture_name, query, idx) -> None:
    data = request.getfixturevalue(fixture_name)
    result = search(data, query)

    if isinstance(data, pl.DataFrame):
        expected = data[idx]
        polars.testing.assert_frame_equal(result, expected)
    else:
        expected = data.iloc[idx]
        pd.testing.assert_frame_equal(result, expected)

