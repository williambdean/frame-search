# Frame Search

A GitHub search inspired interface to DataFrames.

Powered by [`narwhals`](https://narwhals-dev.github.io/narwhals/).

## Features

| Feature Category | Feature | Description | Example |
|------------------|---------|-------------|---------|
| **Search Syntax** | Key-Value Search | Search specific columns using key:value syntax | `name:alice` |
| | Comparison Operators | Support for `>`, `<`, `>=`, `<=` operators | `age:>30`, `price:<=100` |
| | Range Search | Search within ranges using `..` syntax | `age:25..35`, `date:2023-01-01..2023-12-31` |
| | Quoted Strings | Exact phrase matching with quotes | `city:"New York"`, `title:"Data Science"` |
| | Standalone Terms | Search default column without key | `alice` (searches default column) |
| | Combined Queries | Multiple conditions with implicit AND | `age:>25 city:"New York"` |
| **DataFrame Support** | Pandas DataFrames | Native `.search()` method for pandas | `df.search("name:alice")` |
| | Polars DataFrames | Native `.search()` method for polars | `df.search("age:>30")` |
| | Polars LazyFrames | Lazy evaluation support | `df.lazy().search("city:chicago").collect()` |
| | Pipe Function | Use with pandas pipe | `df.pipe(search_func, "query")` |
| **Data Types** | String Matching | Case-insensitive contains search | `name:alice` matches "Alice Smith" |
| | Numeric Comparison | Integer and float comparisons | `age:25`, `price:99.99` |
| | Date Support | YYYY-MM-DD date parsing and comparison | `date:2023-01-01`, `created:>2023-06-01` |
| | Range Operations | Bounded and unbounded ranges | `*..100` (≤100), `50..*` (≥50) |
| **Configuration** | Column Mapping | Map search keys to actual column names | `{"name": "full_name", "age": "current_age"}` |
| | Default Column | Set default column for standalone searches | `default="description"` |
| | Schema Awareness | Automatic data type detection | Uses DataFrame schema for type inference |
| **Integrations** | Marimo Notebooks | Interactive search UI components | `mo.ui.text()` with `.search()` |
| | Cross-Library | Works with any narwhals-supported library | pandas, polars, and more |

## Installation

Install from PyPI:

```terminal
uv add frame-search
```

## Usage

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

# Internal API

```python
from frame_search import create_search

search = create_search("Name", {"name": "Full Name", "age": "Current Age", "Hometown": "city"})
```


This search function will work on any DataFrame library supported by `narwhals`. For example, pandas:

```python
import pandas as pd

df = pd.DataFrame({
    "Full Name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "Current Age": [25, 30, 35],
    "Hometown": ["New York", "Los Angeles", "Chicago"]
})

df.pipe(search, "name:alice age:>30 hometown:miami")
```

Or use the `search` property of pandas and polars Frames:

```python
import pandas as pd

# Adds `search` property to DataFrames
import frame_search  # noqa: F401

df = pd.DataFrame({
    "Full Name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "Current Age": [25, 30, 35],
    "Hometown": ["New York", "Los Angeles", "Chicago"]
})

query = "name:alice age:>30 hometown:miami"
df.search(query)

df_pl = pl.DataFrame(df)
df_pl.search(query)
df_pl.lazy().search(query).collect()
```
