# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import pandas as pd

    from frame_search.data import data

    return data, mo, pd


@app.cell
def _(mo):
    mo.md(
        """
    # Frame Search

    A GitHub search inspired interface to DataFrames.

    Powered by [`narwhals`](https://narwhals-dev.github.io/narwhals/).

    ## Features

    By importing `frame_search`, DataFrames gain a `search` method that
    can be used to filter rows based on a search query string.

    ```python
    import frame_search  # noqa: F401

    df.search("<your-search-query>")
    ```

    Each query string can include:

    - equality: `column:value`
        - booleans: `is:column`, `has:column`, `column:true`, `column:false`
    - string contains: `column:almost_value`
    - string union: `column:value1,value2`
    - inequality: `column:>value`, `column:<value`, `column:>=value`, `column:<=value`
    - range: `column:lower..upper`, `column:lower..*`, `column:*..upper`
    - negatation: `-expr`, `NOT expr`
    - Logical AND: `expr1 expr2 expr3`


    ## Search Syntax References

    - [Cheatsheet](https://gist.github.com/bonniss/4f0de4f599708c5268134225dda003e0)
    - [GitHub Docs](https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax)
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ## Example

    Consider the following dataset:
    """
    )
    return


@app.cell
def _(data, pd):
    # Create a small example dataset inspired by tests/
    df = pd.DataFrame(data)
    df
    return (df,)


@app.cell
def _(mo):
    search = mo.ui.text(
        label="Search Query: ",
        value='city:"New York" score:>85',
        full_width=True,
    )
    map_columns = mo.ui.checkbox(label="Map Column Names", value=False)
    use_default_column = mo.ui.checkbox(label="Use Default Column", value=False)

    mo.vstack(
        [
            search,
            mo.hstack(
                [
                    mo.md("Additional keyword arguments:"),
                    map_columns,
                    use_default_column,
                ],
                justify="start",
            ),
        ]
    )
    return map_columns, search, use_default_column


@app.cell
def _(map_columns, mo, search, use_default_column):
    quote = "'" if search.value.find('"') != -1 else '"'

    if map_columns.value:
        mapping_to_columns = {"math_major": "Math Major"}
        kwargs = f", mapping_to_columns={mapping_to_columns}"
    else:
        mapping_to_columns = None
        kwargs = ""

    if use_default_column.value:
        default = "city"
        kwargs = f'{kwargs}, default="{default}"'
    else:
        default = None
        kwargs = f"{kwargs}"

    mo.md(
        f"""
    ```python
    import frame_search  # noqa: F401

    # Your DataFrame from pandas, polars, pyspark, etc.
    df = ...

    df.search({quote}{search.value}{quote}{kwargs})
    ```
    """
    )
    return default, mapping_to_columns


@app.cell
def _(default, df, mapping_to_columns, mo, search):
    try:
        result = mo.vstack(
            [
                mo.md("This gives the following DataFrame:"),
                df.search(
                    search.value, mapping_to_columns=mapping_to_columns, default=default
                ),
            ]
        )
    except Exception as e:
        result = mo.callout(f"{type(e).__name__}: {e}")

    result
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
