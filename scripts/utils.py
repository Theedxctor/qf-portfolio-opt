# scripts/utils.py
import pandas as pd
from typing import List

def get_sp500_tickers() -> List[str]:
    """
    Fetches the S&P 500 list from a maintained GitHub CSV.
    This is much more stable than scraping Wikipedia directly.
    """
    # This URL is maintained by the 'datasets' community on GitHub
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    
    print(f"Fetching tickers from curated CSV: {url}")
    
    try:
        # Pandas can read a CSV directly from a URL!
        df = pd.read_csv(url)
        
        # In this CSV, the column is usually named 'Symbol'
        if 'Symbol' in df.columns:
            tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
            print(f"SUCCESS: Found {len(tickers)} tickers.")
            return tickers
        else:
            print(f"Error: 'Symbol' column not found. Columns are: {df.columns.tolist()}")
            return []
            
    except Exception as e:
        print(f"Failed to fetch CSV: {e}")
        return []