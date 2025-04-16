import os

import requests
import pandas as pd
import io
from dotenv import load_dotenv

from TickerData import TickerData

# Load variables from .env into the environment
load_dotenv()

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if API_KEY is None:
    raise Exception("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file.")


class Tickers:
    def __init__(self):
        self.data = self._get_ticker_data()

    def _get_all_tickers(self):
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={API_KEY}'
        response = requests.get(url)

        # Check that the response was successful.
        if response.status_code != 200:
            raise Exception(f"API request unsuccessful: HTTP {response.status_code}")

        # Parse the CSV data from the response text.
        tickers_df = pd.read_csv(io.StringIO(response.text))
        return tickers_df

    def _get_ticker_data(self):
        """
            Creates a hash map (dictionary) of ticker symbols to TickerData instances.

            Returns:
                A dictionary with ticker symbols as keys and TickerData instances as values.
            """
        tickers_df = self._get_all_tickers()
        ticker_map = {}

        # Iterate through each row in the DataFrame and create a TickerData object.
        for _, row in tickers_df.iterrows():
            # The CSV from Alpha Vantage is expected to have the following columns:
            # "symbol", "name", "exchange", "assetType", "ipoDate", "delistingDate", "status"
            symbol = row['symbol']
            name = row['name']
            exchange = row['exchange']
            asset_type = row['assetType']
            ipo_date = row['ipoDate']
            delisting_date = row['delistingDate']
            status = row['status']

            ticker_data = TickerData(symbol, name, exchange, asset_type, ipo_date, delisting_date, status)
            ticker_map[symbol] = ticker_data

        return ticker_map
