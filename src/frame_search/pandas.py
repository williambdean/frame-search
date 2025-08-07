import pandas as pd

from frame_search.extension import BaseSearchAccessor


@pd.api.extensions.register_dataframe_accessor("search")
class SearchAccessor(BaseSearchAccessor):
    """A pandas DataFrame accessor for search functionality.

    This accessor provides methods to search for specific values in a DataFrame
    and return the rows that contain those values.

    Examples
    --------

    .. code-block:: python

        import pandas as pd

        import frame_search  # noqa: F401

        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['apple', 'banana', 'cherry']
        })

        df.search("A:>1")

    """
