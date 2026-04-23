# tables/stock_price.py
from datetime import datetime
from sqlalchemy import DateTime, Float, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from tables import Base

class StockPriceDataset(Base):
    __tablename__ = "stock_price_dataset"

    # We use a composite primary key (Date + Asset) 
    # so we can't have duplicate entries for the same stock on the same day.
    date: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    asset: Mapped[str] = mapped_column(String, primary_key=True)
    
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    
    # Note: I'm using BigInteger as we discussed, to handle high-volume stocks!
    volume: Mapped[int] = mapped_column(BigInteger)
    dividends: Mapped[float] = mapped_column(Float)
    stock_split: Mapped[float] = mapped_column(Float)