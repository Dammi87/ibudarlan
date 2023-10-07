import os
import pickle
import pandas as pd
from datetime import datetime


class DataframeCacher:
    def __init__(self, prefix: str, cache_dir='.'):
        self.prefix = prefix
        self.cache_dir = cache_dir

    @property
    def cache_file(self):
        """Get the filename for the cache file."""
        current_month = datetime.now().strftime("%Y-%m")
        return os.path.join(self.cache_dir, f"{self.prefix}-{current_month}.pickle")

    def has_cache(self):
        """Check if the cached data is up-to-date."""
        current_month = datetime.now().strftime("%Y-%m")
        cache_file = self.cache_file
        return os.path.exists(cache_file) and cache_file.endswith(f"{current_month}.pickle")

    def load(self) -> pd.DataFrame:
        """Load the cache from disk."""
        if self.has_cache():
            print(f"Loading {self.prefix} data from cache.")
            with open(self.cache_file, "rb") as f:
                try:
                    return pickle.load(f)
                except pickle.UnpicklingError:
                    pass
        return None

    def save(self, dataframe: pd.DataFrame):
        """Save the cache to disk."""
        with open(self.cache_file, "wb") as f:
            print(f"Saving {self.prefix} data to cache.")
            pickle.dump(dataframe, f)
