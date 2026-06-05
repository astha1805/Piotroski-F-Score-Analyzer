import os
import time
import requests
import pandas as pd
from f_score import calculate_piotroski_f_score
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AV_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

REQUIRED_FIELDS = {
    
    # Net Income is used for ROA (Return on Assets) = Net Income / Total Assets (If ROA > 0, it means company is profitable)

    # Total Revenue is used for Asset Turnover = Revenue / Total Assets (Tells us how efficiently company uses assets to generate sales)

    # Gross Profit is used for Gross Margin = Gross Profit / Revenue (Tells us whether company os earning more profit per rupee / dollar of sales)
    
    "INCOME_STATEMENT" : [
        "fiscalDateEnding",
        "totalRevenue",
        "grossProfit",
        "netIncome"
    ],
    
    # Total Assets are the denominators for many rations

    # Current Assets are used for Current Ratio = Current Assets / Current Liabilities (Measures short-term liquidity)

    # Current Liabilities tells us the company's short-term obligations

    # Long Term debt is used for Leverage Ratio = Long Term Debt / Total Assets

    # Total Stock Holders Equity is used for BM (Book-to-Market Ratio) = Book Equity / Market Equity

    # Common Stock is used to detect whether company issued new equity (If company issued new shares, bad signal for distressed firms)
    
    "BALANCE_SHEET" : [
        "fiscalDateEnding",
        "totalAssets",
        "totalCurrentAssets",
        "totalCurrentLiabilities",
        "longTermDebt",
        "totalShareholderEquity",
        "commonStockSharesOutstanding"
    ],

    # Operating Cash Flow is used for CFO signal = Operating Cash Flow / Total Assets
    
    "CASH_FLOW" : [
        "fiscalDateEnding",
        "operatingCashflow"
    ]
}

COLUMN_MAPPING = {
    "fiscalDateEnding" : "fiscal_date",
    "totalRevenue" : "revenue",
    "grossProfit" : "gross_profit",
    "netIncome" : "net_income",
    "totalAssets" : "total_assets",
    "totalCurrentAssets" : "current_assets",
    "totalCurrentLiabilities" : "current_liabilities",
    "longTermDebt" : "long_term_debt",
    "totalShareholderEquity" : "shareholder_equity",
    "commonStockSharesOutstanding" : "shares_outstanding",
    "operatingCashflow" : "operating_cashflow"
}

def clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Converting Alpha Vantage numeric columns from strings to numbers

    df = df.copy()

    for col in df.columns:
        if col != "fiscal_date":
            df[col] = pd.to_numeric(df[col], errors = "coerce")

    return df

def fetch_alpha_vantage(function_name: str, ticker: str) -> pd.DataFrame:
    """
    Fetch financial statement data from Alpha Vantage.
    function_name can be:
    - INCOME_STATEMENT
    - BALANCE_SHEET
    - CASH_FLOW
    """

    params = {
        "function": function_name,
        "symbol": ticker,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")

    data = response.json()

    if "Note" in data:
        raise Exception(f"API limit reached: {data['Note']}")

    if "Error Message" in data:
        raise Exception(f"API error: {data['Error Message']}")

    if "annualReports" not in data:
        raise Exception(f"Unexpected response format: {data}")

    df = pd.DataFrame(data["annualReports"])

    required_cols = REQUIRED_FIELDS[function_name]
    df = df[required_cols]

    df = df.rename(columns = COLUMN_MAPPING)

    df["fiscal_date"] = pd.to_datetime(df["fiscal_date"])

    df = clean_numeric_columns(df)

    return df

def get_financials_for_ticker(ticker: str) -> pd.DataFrame:
    income_statement = fetch_alpha_vantage("INCOME_STATEMENT", ticker)
    balance_sheet = fetch_alpha_vantage("BALANCE_SHEET", ticker)
    cash_flow = fetch_alpha_vantage("CASH_FLOW", ticker)

    merged = income_statement.merge(
        balance_sheet,
        on = "fiscal_date",
        how = "inner"
    )

    merged = merged.merge(
        cash_flow,
        on = "fiscal_date",
        how = "inner"
    )

    merged["ticker"] = ticker
    merged = merged.sort_values("fiscal_date").reset_index(drop=True)

    return merged

def get_financials_for_multiple_tickers(tickers: list, sleep_time: int = 15) -> pd.DataFrame:
    all_financials = []

    for ticker in tickers:
        try:
            print(f"Fetching data for {ticker}...")
            df = get_financials_for_ticker(ticker)
            all_financials.append(df)

            time.sleep(sleep_time)

        except Exception as e:
            print(f"Failed for {ticker}: {e}")

    if not all_financials:
        return pd.DataFrame()
    
    combined = pd.concat(all_financials, ignore_index = True)

    return combined

if __name__ == "__main__":
    test_tickers = ["AAPL", "MSFT"]

    financials = get_financials_for_multiple_tickers(test_tickers)

    print(financials.head())
    print(financials.info())

    financials.to_csv("combined_financials.csv", index=False)

    print("Data collection successful.")
    
    """aapl_scores = scored_financials[scored_financials["ticker"] == "AAPL"].copy()

    prices = fetch_price_data(
        ticker="AAPL",
        start_date="2006-01-01",
        end_date="2026-12-31"
    )

    aapl_scores["portfolio_start_date"] = aapl_scores["fiscal_date"].apply(
        calculate_portfolio_start_date
    )

    aapl_scores["one_year_forward_return"] = aapl_scores["portfolio_start_date"].apply(
        lambda date: calculate_forward_return(prices, date, holding_months=12)
    )

    print(aapl_scores[[
        "ticker",
        "fiscal_date",
        "f_score",
        "portfolio_start_date",
        "one_year_forward_return"
    ]])"""