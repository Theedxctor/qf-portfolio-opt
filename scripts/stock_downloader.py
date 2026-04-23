# scripts/stock_downloader.py
import logging
import random
import time

import pandas as pd
import yfinance as yf


class StockDownloader:
    def download_history(self, ticker: str) -> pd.DataFrame:
        try:
            # 1. Add Jitter: Wait between 2.0 and 4.5 seconds
            wait_time = random.uniform(2.0, 4.5)
            time.sleep(wait_time)

            # 2. Download (curl_cffi handles the TLS fingerprinting automatically)
            stock = yf.Ticker(ticker)
            df = stock.history(period="max")

            if df.empty:
                return pd.DataFrame()

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            return df

        except Exception as e:
            logging.error(f"Error on {ticker}: {e}")
            return pd.DataFrame()
