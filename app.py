import streamlit as st
import pandas as pd

from data_collection import get_financials_for_multiple_tickers
from f_score import calculate_piotroski_f_score
from analysis import (
    add_forward_returns,
    summarize_by_f_score,
    summarize_by_bucket
)


DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "TSLA", "JPM", "BAC", "V",
    "MA", "WMT", "PG", "KO", "PEP",
    "DIS", "NFLX", "INTC", "CSCO", "ORCL"
]


st.set_page_config(
    page_title="Piotroski F-Score Analyzer",
    layout="wide"
)

st.title("Piotroski F-Score Value Investing Analyzer")

st.write(
    "This app calculates Piotroski F-Scores using financial statement data "
    "and compares them with future 1-year stock returns."
)

tickers_input = st.text_area(
    "Enter stock tickers separated by commas",
    value=", ".join(DEFAULT_TICKERS)
)

tickers = [
    ticker.strip().upper()
    for ticker in tickers_input.split(",")
    if ticker.strip()
]

sleep_time = st.slider(
    "API delay between Alpha Vantage calls",
    min_value=5,
    max_value=30,
    value=15
)

if st.button("Run Analysis"):
    with st.spinner("Fetching financial statements..."):
        combined_financials = get_financials_for_multiple_tickers(
            tickers,
            sleep_time=sleep_time
        )

    if combined_financials.empty:
        st.error("No financial statement data found.")
        st.stop()

    with st.spinner("Calculating Piotroski F-Scores..."):
        scored_financials = calculate_piotroski_f_score(combined_financials)

    with st.spinner("Fetching market prices and calculating forward returns..."):
        final_df = add_forward_returns(scored_financials)

    if final_df.empty:
        st.error("Could not calculate forward returns.")
        st.stop()

    final_df = final_df.dropna(subset=["one_year_forward_return"])

    st.success("Analysis complete.")

    st.subheader("Final Dataset")
    st.dataframe(final_df[[
        "ticker",
        "fiscal_date",
        "f_score",
        "portfolio_start_date",
        "one_year_forward_return",
        "roa",
        "cfo",
        "leverage",
        "current_ratio",
        "gross_margin",
        "asset_turnover"
    ]])

    st.subheader("Average Forward Return by F-Score")
    score_summary = summarize_by_f_score(final_df)
    st.dataframe(score_summary)

    st.bar_chart(
        score_summary.set_index("f_score")["avg_forward_return"]
    )

    st.subheader("Average Forward Return by Score Bucket")
    bucket_summary = summarize_by_bucket(final_df)
    st.dataframe(bucket_summary)

    st.bar_chart(
        bucket_summary.set_index("score_bucket")["avg_forward_return"]
    )

    st.subheader("F-Score vs One-Year Forward Return")
    st.scatter_chart(
        final_df,
        x="f_score",
        y="one_year_forward_return"
    )

    st.subheader("Download Results")

    csv = final_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download final dataset as CSV",
        data=csv,
        file_name="piotroski_f_score_results.csv",
        mime="text/csv"
    )