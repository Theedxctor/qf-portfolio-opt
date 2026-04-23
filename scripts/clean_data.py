# scripts/clean_data.py

import pandas as pd
from sqlalchemy import create_engine


def clean_financial_data():
    db_url = "postgresql://devdocker:devpassword@localhost:5432/qffun"
    engine = create_engine(db_url)

    print("Loading returns for cleaning...")
    # Load the returns we calculated earlier
    df = pd.read_sql("SELECT * FROM stock_returns", engine)

    # 1. Pivot to "Wide Format" (Dates as rows, Assets as columns)
    pivot_df = df.pivot(index="date", columns="asset", values="log_return")

    # 2. Handle Time-Alignment (The "Informatics" decision)
    # We only want data from when 'most' stocks existed.
    # Let's truncate to the last 10 years (approx 2520 trading days)
    # This ensures your RL model isn't trying to learn from the 1960s.
    pivot_df = pivot_df.tail(2520)

    # 3. Handle Missing Values
    # We drop any stock that still has more than 5% missing data in this window
    limit = len(pivot_df) * 0.95
    pivot_df = pivot_df.dropna(axis=1, thresh=limit)

    # For the remaining small gaps, we use 'Forward Fill' (carry the last return forward)
    # then 'Fill Zero' for anything left.
    pivot_df = pivot_df.ffill().fillna(0)

    # 4. Outlier Removal (Winsorization)
    # We cap returns at 3 standard deviations to prevent 'flash crashes' from ruining the ML
    for col in pivot_df.columns:
        mu = pivot_df[col].mean()
        sigma = pivot_df[col].std()
        pivot_df[col] = pivot_df[col].clip(mu - 3 * sigma, mu + 3 * sigma)

    print(f"Cleaning complete. Remaining assets: {len(pivot_df.columns)}")

    # 5. Save the 'Final' clean data for the RL Model
    # Melting back to long format for the DB
    clean_df = pivot_df.reset_index().melt(id_vars="date", var_name="asset", value_name="clean_return")
    clean_df.to_sql("stock_returns_clean", engine, if_exists="replace", index=False)

    print("Saved to 'stock_returns_clean'.")


if __name__ == "__main__":
    clean_financial_data()
