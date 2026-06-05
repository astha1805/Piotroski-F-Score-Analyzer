import yfinance as yf
import pandas as pd
from dateutil.relativedelta import relativedelta

def fetch_price_data(ticker: str, start_date:str, end_date: str) -> pd.DataFrame:
    """
    Historical price data from Yahoo finance
    """
    price_data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        progress = False,
        auto_adjust=True
    )

    if price_data.empty:
        return pd.DataFrame()
    
    if isinstance(price_data.columns, pd.MultiIndex):
        price_data.columns = price_data.columns.get_level_values(0)
        
    price_data = price_data.reset_index()

    price_data["ticker"] = ticker

    price_data = price_data[["Date", "ticker", "Close"]]

    price_data = price_data.rename(
        columns={
            "Date" : "date",
            "Close" : "close_price"
        }
    )

    return price_data


def calculate_portfolio_start_date(fiscal_date):
    """
    Piotroski starts return measurement from beginning of the fifth month 
    after fiscal year-end
    """
    fiscal_date = pd.to_datetime(fiscal_date)

    portfolio_start = fiscal_date + relativedelta(months=4)

    return portfolio_start

def calculate_forward_return(
        prices: pd.DataFrame,
        start_date,
        holding_months: int = 12
):
    """
    Calculate buy-and-hold forward return from portfolio start date
    to holding_months later.

    Uses the nearest available trading day on or after the target dates.
    """

    prices = prices.copy()
    prices["date"] = pd.to_datetime(prices["date"])
    prices = prices.sort_values("date").reset_index(drop=True)

    start_date = pd.to_datetime(start_date)
    end_date = start_date + relativedelta(months=holding_months)

    # Finding first trading day on or after start_date
    start_prices = prices[prices["date"] >= start_date]
    if start_prices.empty:
        return None
    
    start_row = start_prices.iloc[0]
    start_price = start_row["close_price"]

    # Finding first trading day on or after end_date
    end_prices = prices[prices["date"] >= end_date]

    if end_prices.empty:
        return None
    
    end_row = end_prices.iloc[0]
    end_price = end_row["close_price"]

    forward_return = (end_price - start_price) / start_price

    return forward_return

