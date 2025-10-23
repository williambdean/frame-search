# Frame Search

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/williambdean/frame-search/actions/workflows/tests.yml/badge.svg)](https://github.com/williambdean/frame-search/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/frame-search.svg)](https://badge.fury.io/py/frame-search)

A GitHub search inspired interface to DataFrames.

Powered by [`narwhals`](https://narwhals-dev.github.io/narwhals/).

## Installation

Install from PyPI:

```terminal
uv add frame-search
```

## Usage

### API

Importing `frame_search` adds a `search` properties to pandas and polars objects.

```python
# Import to add `search` property to DataFrames
import frame_search  # noqa: F401

import polars as pl

df = pl.DataFrame({
    "name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "age": [25, 30, 35],
    "hometown": ["New York", "New York", "Chicago"]
})

df.search('age:<30 hometown:"New York"')
```

```text
shape: (1, 3)
┌─────────────┬─────┬──────────┐
│ name        ┆ age ┆ hometown │
│ ---         ┆ --- ┆ ---      │
│ str         ┆ i64 ┆ str      │
╞═════════════╪═════╪══════════╡
│ Alice Smith ┆ 25  ┆ New York │
└─────────────┴─────┴──────────┘
```

### Interactive Search in Marimo Notebooks

Use with [`marimo`](https://marimo.io/) to create a search interface for DataFrames:

```python
import marimo as mo

search = mo.ui.text(label="DataFrame Search Query:")
search
```

Then use on a DataFrame:

```python
import polars as pl

import frame_search  # noqa: F401

df = pl.DataFrame({
    "name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "age": [25, 30, 35],
    "hometown": ["New York", "Los Angeles", "Chicago"]
})

df_filter = df.search(search.value)

df_filter
```

Here is another example in a Marimo notebook:

![Marimo Example](./images/marimo-example.png)

## Search Syntax

The search syntax is inspired by GitHub's search syntax. Here are some resources:

- [Cheatsheet](https://gist.github.com/bonniss/4f0de4f599708c5268134225dda003e0)
- [GitHub Docs](https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax)

Not all syntax features are currently supported. View the [GitHub issues](https://github.com/williambdean/frame-search/issues) for planned features or to request new ones.

## Features

| Feature | Syntax | Example | Status |
|---------|--------|---------|--------|
| **Text Search** | `column:value` | `name:alice` | ✅ Supported |
| **Case-Insensitive Search** | `column:value` | `name:Alice` → matches "alice" | ✅ Supported |
| **Quoted Strings** | `column:"exact value"` | `city:"New York"` | ✅ Supported |
| **Default Column Search** | `value` | `alice` (searches default column) | ✅ Supported |
| **Numeric Comparisons** |  |  |  |
| - Greater Than | `column:>value` | `age:>30` | ✅ Supported |
| - Less Than | `column:<value` | `age:<30` | ✅ Supported |
| - Greater or Equal | `column:>=value` | `age:>=30` | ✅ Supported |
| - Less or Equal | `column:<=value` | `age:<=30` | ✅ Supported |
| - Exact Match | `column:value` | `age:35` | ✅ Supported |
| **Range Queries** |  |  |  |
| - Bounded Range | `column:min..max` | `age:30..35` | ✅ Supported |
| - Lower Bound Only | `column:min..*` | `age:30..*` | ✅ Supported |
| - Upper Bound Only | `column:*..max` | `age:*..35` | ✅ Supported |
| **Date/DateTime Support** |  |  |  |
| - Date Comparison | `column:<date` | `first_visit:<2022-01-01` | ✅ Supported |
| - DateTime Comparison | `column:>=datetime` | `created_at:>=2022-01-01T12:00:00` | ✅ Supported |
| - Date Range | `column:start..end` | `first_visit:2022-01-01..2023-12-31` | ✅ Supported |
| **Logical Operators** |  |  |  |
| - Implicit AND | Multiple terms | `age:<30 hometown:"New York"` | ✅ Supported |
| - OR (comma) | `column:val1,val2` | `hobby:reading,sports` | ✅ Supported |
| - OR (pipe) | `column:val1\|val2` | `hobby:reading\|sports` | ✅ Supported |
| - Explicit AND | `term1 AND term2` | `name:alice AND age:>30` | 🚧 Planned ([#19](https://github.com/williambdean/frame-search/issues/19)) |
| - Explicit OR | `term1 OR term2` | `name:alice OR age:>35` | 🚧 Planned ([#20](https://github.com/williambdean/frame-search/issues/20)) |
| **Negation** |  |  |  |
| - Short Form | `-column:value` | `-name:Alice` | ✅ Supported |
| - Long Form | `NOT column:value` | `NOT name:Alice` | ✅ Supported |
| - Range Negation | `-column:min..max` | `-age:30..35` | ✅ Supported |
| - Default Column | `-value` | `-bob` | ✅ Supported |
| **Advanced Features** |  |  |  |
| - Parentheses | `(term1 OR term2) AND term3` | `(name:alice OR age:>35) AND hobby:reading` | 🚧 Planned ([#18](https://github.com/williambdean/frame-search/issues/18)) |
| - Boolean Columns | `is:column` or `has:column` | `is:active` or `has:verified` | 🚧 Planned ([#29](https://github.com/williambdean/frame-search/issues/29)) |

### Notes

- Text searches are **case-insensitive** and use **contains** matching by default
- Numeric and date comparisons support both integers and floats
- Date/datetime values must be in ISO 8601 format
- Multiple conditions without explicit operators are combined with **AND** logic
- The library automatically detects column data types from the DataFrame schema
