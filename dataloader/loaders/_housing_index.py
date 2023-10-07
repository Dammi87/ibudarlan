import pandas as pd
import aiohttp
import requests
from datetime import datetime
from dateutil import parser
from typing import Union
from dataloader.utils import DataframeCacher


class HousingIndexData:
    url = "https://talnaefni.fasteignaskra.is/talnaefni/v1/ibudavisitala"
    cache = DataframeCacher('housing_index')
    data = None
    _df = None

    @classmethod
    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    self.data = await response.json()
                else:
                    raise ValueError(f"Failed to fetch data: {response.status}")

    @classmethod
    def fetch_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.data = response.json()
        else:
            raise ValueError(f"Failed to fetch data: {response.status_code}")

    @classmethod
    def create_dataframe(self):
        self.fetch_data()
        df = pd.DataFrame(self.data, columns=["Ar", "Manudur", "Vst_heild", "Vst_serb", "Vst_fjolb", "Vst_nafnv", "date", "date_month"])
        df = df.rename(columns={"Ar": "year", "Manudur": "month", "Vst_heild": "total", "Vst_serb": "villas", "Vst_fjolb": "apartment", "Vst_nafnv": "adjusted"})
        dtypes = {"year": "int", "month": "int", "total": "float", "villas": "float", "apartment": "float", "adjusted": "float", "date": "datetime64[ns]", "date_month": "datetime64[ns]"}
        df = df.astype(dtypes)
        df["housing_index"] = (df["adjusted"] - df["adjusted"].shift(1)) / df["adjusted"].shift(1)
        df.loc[0, "housing_index"] = 0
        return df

    @classmethod
    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            if self.cache.has_cache():
                self._df = self.cache.load()
            else:
                self._df = self.create_dataframe()
                self.cache.save(self._df)
        return self._df

    @classmethod
    def index_at(self, date: Union[datetime, str]) -> float:
        if isinstance(date, str):
            date = parser.parse(date)
        return self.df.loc[self.df["date"] == date, "housing_index"].iloc[0]

    @classmethod
    def join_at(self, df: pd.DataFrame, date_column: str):
        # Create new columns with year and month only
        df["year_month"] = df[date_column].dt.strftime("%Y-%m")
        self.df["year_month"] = self.df["date"].dt.strftime("%Y-%m")

        # Join the dataframes on the year_month column
        df = pd.merge(df, self.df[['year_month', 'housing_index']], how="inner", left_on="year_month", right_on="year_month")
        return df.drop("year_month", axis=1)
