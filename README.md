# Frame Search

A GitHub search inspired interface to DataFrames.

Powered by `narwhals`.

```python
# Import to add `search` property to DataFrames
import frame_search # noqa: F401

import polars as pl

df = pl.DataFrame({
    "name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "age": [25, 30, 35],
    "hometown": ["New York", "New York", "Chicago"]
})

df.search("age:<30 hometown:New York")
```


# Internal API

```python
from frame_search import create_search

search = create_search("Name", {"name": "Full Name", "age": "Current Age", "Hometown": "city"})
```


```python
import pandas as pd
df = pd.DataFrame({
    "Full Name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "Current Age": [25, 30, 35],
    "Hometown": ["New York", "Los Angeles", "Chicago"]
})


df.pipe(search, "name:alice age:>30 hometown:miami")
```

Or use the `search` property of DataFrames:

```python
import pandas as pd

# Adds `search` property to DataFrames
import frame_search

df = pd.DataFrame({
    "Full Name": ["Alice Smith", "Bob J. Dawkins", "Charlie Brown"],
    "Current Age": [25, 30, 35],
    "Hometown": ["New York", "Los Angeles", "Chicago"]
})


df.search("name:alice age:>30 hometown:miami")
```
