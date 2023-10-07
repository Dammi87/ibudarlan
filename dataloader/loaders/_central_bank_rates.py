import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import os
import pandas as pd
from datetime import datetime
from typing import Union
from dataloader.utils import DataframeCacher



class CentralBankInterestsData:
    
    url = "https://px.hagstofa.is/pxis/sq/50fced24-a043-49ab-aa02-38ef32285179?v={unix_time}"
    cache = DataframeCacher('central_index')
    data = None
    _df = None

    @classmethod
    def fetch_data(self):
        # Set download options
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": os.getcwd()}
        options.add_experimental_option("prefs", prefs)

        # Set up the webdriver and navigate to the page
        chrome_service = Service('C:/tools/chromedriver/chromedriver.exe')
        browser = webdriver.Chrome(service=chrome_service, options=options)
        url = f"https://www.gagnabanki.is/report/interests?from=2007-01-01&to={datetime.today().strftime('%Y-%m-%d')}&select=24,28,17923&view=chart"
        browser.get(url)

        # Locate the download button (modify the selector to match your actual button)
        selector = "body > app-root > div > div.main > app-report > div > div > div.content > div.page-header > div.filter-panel-content > div:nth-child(4) > button"
        button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        button.click()

        # Wait for the download to complete (this is a bit tricky; you might need to monitor the download directory for a new file)
        time.sleep(10)  # Or however long you expect the download to take

        # After you've confirmed the download is complete, close the browser
        browser.quit()

        df = pd.read_csv("Meginvextir.csv", ";", usecols=[0, 3], decimal=",")
        df.columns = ["date", "central_interest_rate"]
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        df["central_interest_rate"] /= 100.0
        os.remove("Meginvextir.csv")

        return df

    @classmethod
    @property
    def df(self):
        if self._df is not None:
            return self._df

        if self.cache.has_cache():
            self._df = self.cache.load()
        else:
            self._df = self.fetch_data()
            self.cache.save(self._df)
        return self._df

    @classmethod
    def index_at(self, date: Union[datetime, str]) -> float:
        if isinstance(date, str):
            date = parser.parse(date)
        return self.df.loc[self.df["date"] == date, "central_interest_rate"].iloc[0]
