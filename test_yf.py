# test_yf.py
import yfinance as yf

print("Testing AAPL download with modern yfinance...")
try:
    # We don't pass a session; yf will now use curl_cffi automatically
    stock = yf.Ticker("AAPL")
    df = stock.history(period="5d")

    if not df.empty:
        print("SUCCESS! Data received:")
        print(df.tail())
    else:
        print("FAILURE: Dataframe is empty. Yahoo might still be blocking.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")