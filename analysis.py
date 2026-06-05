import pandas as pd

from market_data import (
    fetch_price_data,
    calculate_portfolio_start_date,
    calculate_forward_return
)


def add_forward_returns(scored_financials: pd.DataFrame) -> pd.DataFrame:
    df = scored_financials.copy()

    df["portfolio_start_date"] = df["fiscal_date"].apply(
        calculate_portfolio_start_date
    )

    all_results = []

    for ticker in df["ticker"].unique():
        ticker_df = df[df["ticker"] == ticker].copy()

        start_date = ticker_df["portfolio_start_date"].min()
        end_date = ticker_df["portfolio_start_date"].max() + pd.DateOffset(months=13)

        prices = fetch_price_data(
            ticker=ticker,
            start_date=str(start_date.date()),
            end_date=str(end_date.date())
        )

        if prices.empty:
            continue

        ticker_df["one_year_forward_return"] = ticker_df["portfolio_start_date"].apply(
            lambda date: calculate_forward_return(
                prices,
                date,
                holding_months=12
            )
        )

        all_results.append(ticker_df)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


def summarize_by_f_score(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.dropna(subset=["one_year_forward_return"])

    summary = (
        clean_df
        .groupby("f_score")
        .agg(
            avg_forward_return=("one_year_forward_return", "mean"),
            median_forward_return=("one_year_forward_return", "median"),
            observations=("one_year_forward_return", "count")
        )
        .reset_index()
    )

    return summary


def classify_score_bucket(score: int) -> str:
    if score >= 7:
        return "High F-Score"
    elif score <= 3:
        return "Low F-Score"
    else:
        return "Medium F-Score"


def summarize_by_bucket(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.dropna(subset=["one_year_forward_return"]).copy()

    clean_df["score_bucket"] = clean_df["f_score"].apply(classify_score_bucket)

    summary = (
        clean_df
        .groupby("score_bucket")
        .agg(
            avg_forward_return=("one_year_forward_return", "mean"),
            median_forward_return=("one_year_forward_return", "median"),
            observations=("one_year_forward_return", "count")
        )
        .reset_index()
    )

    return summary