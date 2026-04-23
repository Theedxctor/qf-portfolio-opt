# scripts/populate_database.py
import datetime
import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from scripts.stock_downloader import StockDownloader
from scripts.utils import get_sp500_tickers
from tables.stock_price import StockPriceDataset

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def populate():
    db_url = "postgresql://devdocker:devpassword@localhost:5432/qffun"
    engine = create_engine(db_url)
    downloader = StockDownloader()

    tickers = get_sp500_tickers()
    if not tickers:
        return

    for ticker in tickers:
        print(f"--- Processing {ticker} ---")

        with Session(engine) as session:
            # Fetch existing dates and normalize them to be 100% safe
            existing_dates = session.execute(select(StockPriceDataset.date).filter_by(asset=ticker)).scalars().all()

            # Normalize to naive UTC (Remove TZ info for comparison)
            existing_dates_set = set()
            for d in existing_dates:
                if d.tzinfo:
                    existing_dates_set.add(d.astimezone(datetime.timezone.utc).replace(tzinfo=None))
                else:
                    existing_dates_set.add(d)

        df = downloader.download_history(ticker)
        if df.empty:
            continue

        with Session(engine) as session:
            new_records = 0
            objects_to_add = []

            for date, row in df.iterrows():
                # 1. Normalize the loop date to match the DB format (UTC Naive)
                # This turns '00:00-05:00' into '05:00' then strips the '+00:00'
                if date.tzinfo:
                    check_date = date.tz_convert("UTC").tz_localize(None)
                else:
                    check_date = date

                # 2. Compare using the normalized date
                if check_date in existing_dates_set:
                    continue

                entry = StockPriceDataset(
                    date=check_date,
                    asset=ticker,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                    dividends=float(row["Dividends"]) if "Dividends" in row else 0.0,
                    stock_split=float(row["Stock Splits"]) if "Stock Splits" in row else 0.0,
                )
                objects_to_add.append(entry)
                new_records += 1

            if objects_to_add:
                session.add_all(objects_to_add)
                session.commit()
                print(f"Successfully saved {new_records} new rows for {ticker}")
            else:
                print(f"Skipped {ticker} (Up to date)")


if __name__ == "__main__":
    populate()
