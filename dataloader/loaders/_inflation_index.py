import time
import pandas as pd
import requests
from datetime import datetime
from dateutil import parser
from typing import Union
from dataloader.utils import DataframeCacher


class InflationIndexData:
    
    url = "https://px.hagstofa.is/pxis/sq/50fced24-a043-49ab-aa02-38ef32285179?v={unix_time}"
    cache = DataframeCacher('inflation_index')
    data = None
    _df = None

    @classmethod
    def fetch_data(self):
        unix_time = int(time.time())
        response = requests.get(self.url.format(unix_time=unix_time))
        if response.ok:
            return response.content.decode("ISO-8859-1")
        else:
            raise Exception(f"Error fetching data: {response.status_code}  - {response.reason}")

    @classmethod
    @property
    def df(self):
        if self._df is not None:
            return self._df
        
        if self.cache.has_cache():
            self._df = self.cache.load()
        else:
            # Split the response string into lines and remove the first line
            lines = self.fetch_data().replace('\r', '').replace('"', '').split("\n")[1:-1]

            # Split each line into columns using ";" as the delimiter
            data = [line.split(";") for line in lines]

            # Create a Pandas dataframe from the data list
            self._df = pd.DataFrame(data, columns=["date", "inflation_index"])
            
            dtypes = {"date": "str", "inflation_index": "float"}
            self._df = self._df.astype(dtypes)
    
            self._df['inflation_index'] /= 100.0

            # Define a date_parser function to convert "date" column to a proper datetime object
            date_parser = lambda x: pd.to_datetime("-".join(x.split('M')), format="%Y-%m")

            # Apply the date_parser function to the "date" column of the dataframe
            self._df["date"] = self._df["date"].apply(date_parser)
            self.cache.save(self._df)
        return self._df

    @classmethod
    def index_at(self, date: Union[datetime, str]) -> float:
        if isinstance(date, str):
            date = parser.parse(date)
        return self.df.loc[self.df["date"] == date, "inflation_index"].iloc[0]