import pandas as pd

from frame_search.extension import BaseSearchAccessor


@pd.api.extensions.register_dataframe_accessor("search")
class SearchAccessor(BaseSearchAccessor):
    pass
