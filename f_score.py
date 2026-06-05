import pandas as pd

def calculate_piotroski_f_score(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df = df.sort_values(["ticker", "fiscal_date"]).reset_index(drop=True)
    # Sort by first the company and then the year

    # Finding previous year values for each ticker
    df["prev_roa"] = df.groupby("ticker")["net_income"].shift(1) / df.groupby("ticker")["total_assets"].shift(1)
    df["prev_leverage"] = df.groupby("ticker")["long_term_debt"].shift(1) / df.groupby("ticker")["total_assets"].shift(1)
    df["prev_current_ratio"] = df.groupby("ticker")["current_assets"].shift(1) / df.groupby("ticker")["current_liabilities"].shift(1)
    df["prev_gross_margin"] = df.groupby("ticker")["gross_profit"].shift(1)  / df.groupby("ticker")["revenue"].shift(1)
    df["prev_asset_turnover"] = df.groupby("ticker")["revenue"].shift(1) / df.groupby("ticker")["total_assets"].shift(1)
    df["prev_shares_outstanding"] = df.groupby("ticker")["shares_outstanding"].shift(1)

    # Current year ratios
    df["roa"] = df["net_income"] / df["total_assets"]
    df["cfo"] = df["operating_cashflow"] / df["total_assets"]
    df["leverage"] = df["long_term_debt"] / df["total_assets"]
    df["current_ratio"] = df["current_assets"] / df["current_liabilities"]
    df["gross_margin"] = df["gross_profit"] / df["revenue"]
    df["asset_turnover"] = df["revenue"] / df["total_assets"]

    # 1. PROFITABILITY SIGNALS
    df["F_ROA"] = (df["roa"] > 0).astype(int)
    df["F_CFO"] = (df["cfo"] > 0).astype(int)
    df["F_DELTA_ROA"] = (df["roa"] > df["prev_roa"]).astype(int)
    df["F_ACCRUAL"] = (df["cfo"] > df["roa"]).astype(int)

    # 2. LEVERAGE, LIQUIDITY AND SOURCE OF FUNDS
    df["F_DELTA_LEVERAGE"] = (df["leverage"] < df["prev_leverage"]).astype(int)
    df["F_DELTA_LIQUIDITY"] = (df["current_ratio"] > df["prev_current_ratio"]).astype(int)
    df["F_EQ_OFFER"] = (df["shares_outstanding"] <= df["prev_shares_outstanding"]).astype(int)

    # 3. Operating efficiency
    df["F_DELTA_MARGIN"] = (df["gross_margin"] > df["prev_gross_margin"]).astype(int)
    df["F_DELTA_TURNOVER"] = (df["asset_turnover"] > df["prev_asset_turnover"]).astype(int)

    score_columns = [
        "F_ROA",
        "F_CFO",
        "F_DELTA_ROA",
        "F_ACCRUAL",
        "F_DELTA_LEVERAGE",
        "F_DELTA_LIQUIDITY",
        "F_EQ_OFFER",
        "F_DELTA_MARGIN",
        "F_DELTA_TURNOVER"
    ]

    df["f_score"] = df[score_columns].sum(axis=1)

    return df