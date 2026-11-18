import warnings
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

data_dir = Path(__file__).resolve().parent.parent / "data"


def load_prices(ticker, start="2005-01-01", end=None, refresh=False):
    """Daily adjusted close (splits + dividends) for `ticker`, cached in data/<ticker>.csv.

    `start` is inclusive, `end` exclusive (default: today). The cache is re-downloaded if
    `refresh=True` or it doesn't cover start - end. Rows with missing prices are dropped
    with a warning. Returns a float64 pd.Series named `ticker`, indexed by Date.
    """
    if end is None:
        end = date.today()
    start, end = pd.Timestamp(start), pd.Timestamp(end)

    path = data_dir / f"{ticker}.csv"
    prices = None

    # 1. Try the cache, and throw it away if it doesn't cover start - end
    if path.exists() and not refresh:
        prices = pd.read_csv(path, index_col=0, parse_dates=True).squeeze("columns")
        missing_start = prices.index.min() > start + pd.Timedelta(days=7)
        missing_recent = prices.index.max() < end - pd.offsets.BDay(1)
        if missing_start or missing_recent:
            prices = None

    # 2. No usable cache: download the full requested range and save it untouched
    if prices is None:
        data = yf.download(ticker, start=start, end=end,
                           auto_adjust=True, multi_level_index=False, progress=False)
        if data.empty:
            raise ValueError(f"No price data downloaded for {ticker}")
        prices = data["Close"]
        data_dir.mkdir(parents=True, exist_ok=True)
        prices.to_csv(path, index_label="Date")

    # 3. Normalize, so the cache and download paths return exactly the same thing
    prices = prices.astype("float64").rename(ticker).sort_index()
    prices.index = pd.DatetimeIndex(prices.index).as_unit("s").rename("Date")

    # 4. Missing values: drop them with warning 
    n_missing = prices.isna().sum()
    if n_missing:
        warnings.warn(f"{ticker}: dropped {n_missing} rows with missing prices")
        prices = prices.dropna()

    # 5. Cut to the requested window 
    prices = prices[(prices.index >= start) & (prices.index < end)]
    if prices.empty:
        raise ValueError(f"No {ticker} prices between {start.date()} and {end.date()}")

    return prices


# SPY check
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FixedLocator, NullLocator, StrMethodFormatter

    prices = load_prices("SPY")
    print(prices.describe())

    fig, ax = plt.subplots(figsize=(10,4))
    prices.plot(ax=ax)
    ax.set_yscale("log")
    ax.set_title("SPY adjusted close")
    ax.set_ylabel("Price (USD, log scale)")
    ticks = np.geomspace(prices.min(), prices.max(), 5)
    ticks = [float(f"{t:.2g}") for t in ticks]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:,g}"))
    ax.yaxis.set_minor_locator(NullLocator())
    plt.show()
