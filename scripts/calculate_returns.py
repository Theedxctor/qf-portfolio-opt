# scripts/calculate_returns.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

def calculate_returns():
    db_url = "postgresql://devdocker:devpassword@localhost:5432/qffun"
    engine = create_engine(db_url)
    
    print("Fetching data from database...")
    # 1. Load only the 'close' prices and 'asset' names
    query = "SELECT date, asset, close FROM stock_price_dataset ORDER BY asset, date"
    df = pd.read_sql(query, engine)

    print(f"Processing returns for {df['asset'].nunique()} assets...")

    # 2. Pivot the data so assets are columns and dates are rows
    # This is the 'Quant' way to handle multiple stocks at once
    pivot_df = df.pivot(index='date', columns='asset', values='close')

    # 3. Calculate Log Returns
    # Formula: ln(Price_t / Price_t-1)
    log_returns = np.log(pivot_df / pivot_df.shift(1))

    # 4. Melt the data back to a 'Long' format for the database
    returns_df = log_returns.reset_index().melt(id_vars='date', var_name='asset', value_name='log_return')
    
    # Drop the first row (which will be NaN because there is no 'day before' the first day)
    returns_df = returns_df.dropna()

    print(f"Calculated {len(returns_df)} return points. Saving to DB...")
    
    # 5. Save to a new table (Postgres will create it automatically)
    returns_df.to_sql('stock_returns', engine, if_exists='replace', index=False)
    print("Done! Check the 'stock_returns' table in Adminer.")

if __name__ == "__main__":
    calculate_returns()