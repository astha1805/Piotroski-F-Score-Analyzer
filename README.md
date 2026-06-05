# Piotroski F-Score Value Investing Analyzer

This project implements and analyzes the **Piotroski F-Score**, a fundamental analysis framework introduced by Joseph D. Piotroski in the paper *“Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers.”*

The goal of this project is to test whether accounting-based financial strength signals can help identify stocks with stronger future returns. The project collects financial statement data, calculates Piotroski’s 9-point F-Score, computes one-year forward stock returns, and visualizes the relationship between financial strength and future performance using a Streamlit dashboard.

---

## Project Objective

The original Piotroski paper argues that within value stocks, companies with stronger financial fundamentals tend to outperform financially weak companies. This project recreates the core idea in a modern Python-based workflow.

The project answers:

* Can we calculate Piotroski F-Scores using real financial statement data?
* Do higher F-Scores lead to better one-year forward returns?
* How reliable is the F-Score when applied to a small modern sample of stocks?
* What are the practical limitations of using the F-Score today?

---

## Tech Stack

* Python
* Pandas
* Alpha Vantage API
* Yahoo Finance / yfinance
* Streamlit
* python-dotenv
* dateutil

---

## Project Structure

```text
Piotroski_F-score/
│
├── app.py
├── data_collection.py
├── f_score.py
├── market_data.py
├── analysis.py
├── .env
├── requirements.txt
└── README.md
```

---

## Data Sources

### 1. Alpha Vantage

Alpha Vantage is used to retrieve annual financial statement data.

The following statements are fetched:

#### Income Statement

Used fields:

| Field          | Purpose                            |
| -------------- | ---------------------------------- |
| `netIncome`    | Used to calculate Return on Assets |
| `totalRevenue` | Used to calculate Asset Turnover   |
| `grossProfit`  | Used to calculate Gross Margin     |

#### Balance Sheet

Used fields:

| Field                          | Purpose                                                        |
| ------------------------------ | -------------------------------------------------------------- |
| `totalAssets`                  | Used as denominator for ROA, CFO, leverage, and asset turnover |
| `totalCurrentAssets`           | Used to calculate Current Ratio                                |
| `totalCurrentLiabilities`      | Used to calculate Current Ratio                                |
| `longTermDebt`                 | Used to calculate Leverage                                     |
| `totalShareholderEquity`       | Useful for future book-to-market analysis                      |
| `commonStockSharesOutstanding` | Used to identify whether equity was issued                     |

#### Cash Flow Statement

Used fields:

| Field               | Purpose                                                            |
| ------------------- | ------------------------------------------------------------------ |
| `operatingCashflow` | Used to calculate operating cash flow strength and accrual quality |

---

### 2. Yahoo Finance / yfinance

Yahoo Finance is used to fetch historical adjusted stock prices.

Stock price data is used to calculate:

```text
One-year forward return
```

The forward return is calculated from the portfolio formation date, which is taken as approximately four months after the fiscal year-end. This avoids look-ahead bias because financial statement information is not assumed to be available immediately on the fiscal year-end date.

---

## Piotroski F-Score Methodology

The Piotroski F-Score ranges from 0 to 9.

Each signal receives:

```text
1 = Good signal
0 = Bad signal
```

The final score is the sum of all 9 signals.

---

# Piotroski F-Score Signals

## A. Profitability Signals

### 1. Positive Return on Assets

```text
ROA = Net Income / Total Assets
```

Signal:

```text
F_ROA = 1 if ROA > 0, else 0
```

This checks whether the company is profitable.

---

### 2. Positive Operating Cash Flow

```text
CFO = Operating Cash Flow / Total Assets
```

Signal:

```text
F_CFO = 1 if CFO > 0, else 0
```

This checks whether the company is generating real cash from operations.

---

### 3. Improvement in ROA

```text
ΔROA = Current ROA - Previous Year ROA
```

Signal:

```text
F_DELTA_ROA = 1 if Current ROA > Previous ROA, else 0
```

This checks whether profitability is improving.

---

### 4. Accrual Quality

```text
Accrual Signal = CFO > ROA
```

Signal:

```text
F_ACCRUAL = 1 if CFO > ROA, else 0
```

This checks whether earnings are backed by cash. A company whose operating cash flow is higher than accounting profit is considered to have better earnings quality.

---

## B. Leverage, Liquidity, and Funding Signals

### 5. Decrease in Leverage

```text
Leverage = Long-Term Debt / Total Assets
```

Signal:

```text
F_DELTA_LEVERAGE = 1 if Current Leverage < Previous Leverage, else 0
```

This checks whether the company has reduced debt pressure.

---

### 6. Improvement in Liquidity

```text
Current Ratio = Current Assets / Current Liabilities
```

Signal:

```text
F_DELTA_LIQUIDITY = 1 if Current Ratio > Previous Current Ratio, else 0
```

This checks whether the company’s short-term financial position has improved.

---

### 7. No New Equity Issuance

```text
Shares Outstanding compared with Previous Year Shares Outstanding
```

Signal:

```text
F_EQ_OFFER = 1 if Current Shares Outstanding <= Previous Shares Outstanding, else 0
```

This checks whether the company avoided issuing new shares. Issuing new equity can dilute existing shareholders and may indicate financial weakness.

---

## C. Operating Efficiency Signals

### 8. Improvement in Gross Margin

```text
Gross Margin = Gross Profit / Revenue
```

Signal:

```text
F_DELTA_MARGIN = 1 if Current Gross Margin > Previous Gross Margin, else 0
```

This checks whether the company is earning more profit per unit of revenue.

---

### 9. Improvement in Asset Turnover

```text
Asset Turnover = Revenue / Total Assets
```

Signal:

```text
F_DELTA_TURNOVER = 1 if Current Asset Turnover > Previous Asset Turnover, else 0
```

This checks whether the company is using its assets more efficiently to generate sales.

---

## Final F-Score Formula

```text
F-Score =
F_ROA
+ F_CFO
+ F_DELTA_ROA
+ F_ACCRUAL
+ F_DELTA_LEVERAGE
+ F_DELTA_LIQUIDITY
+ F_EQ_OFFER
+ F_DELTA_MARGIN
+ F_DELTA_TURNOVER
```

A higher score indicates stronger financial health.

Typical interpretation:

| F-Score Range | Interpretation              |
| ------------- | --------------------------- |
| 0–3           | Weak financial position     |
| 4–6           | Moderate financial position |
| 7–9           | Strong financial position   |

---

## Streamlit Dashboard

The project includes a Streamlit dashboard that allows users to:

* Enter stock tickers
* Fetch financial statement data
* Calculate F-Scores
* Calculate one-year forward returns
* View final datasets
* Analyze average forward return by F-Score
* Analyze return by score bucket
* Visualize F-Score vs future return

---

## Graphs and Their Meaning

### 1. Average Forward Return by F-Score

This graph shows the average one-year forward return for each F-Score level.

The expected pattern from the Piotroski paper would be:

```text
Higher F-Score → Higher Average Return
```

However, in this project, the bars may not increase perfectly. This means that the relationship between F-Score and future returns is not perfectly monotonic in the selected sample.

---

### 2. Average Return by Score Bucket

Stocks are grouped into:

| Bucket         | Score Range |
| -------------- | ----------- |
| Low F-Score    | 0–3         |
| Medium F-Score | 4–6         |
| High F-Score   | 7–9         |

This graph compares whether financially strong companies outperform weaker companies on average.

---

### 3. F-Score vs One-Year Forward Return Scatter Plot

Each point represents one company-year observation.

This graph shows how noisy the relationship is between fundamental strength and future returns. A perfect strategy would show higher scores always leading to higher returns, but real stock markets are much more complex.

---

## Observations

The project successfully calculates the Piotroski F-Score and compares it with future stock returns.

However, the graphs do not show a perfectly increasing relationship between F-Score and future returns. This is an important and realistic result.

Possible reasons include:

1. The sample size is small.
2. The selected stocks are mostly large-cap technology and consumer companies.
3. Piotroski originally applied the strategy mainly to high book-to-market value stocks, not all stocks.
4. Large-cap stocks are more efficiently priced.
5. Modern markets process accounting information faster than in the original study period.
6. Stock returns are affected by many non-accounting factors such as interest rates, market sentiment, earnings expectations, macroeconomic shocks, and sector trends.
7. Some accounting data fields may differ slightly across data providers.
8. The strategy uses annual data, while markets react continuously to news.

Therefore, the project should not be interpreted as proof that the F-Score alone can predict returns. Instead, it should be viewed as a research-style implementation of an accounting-based investment framework.

---

## Shortcomings of the Piotroski F-Score

Although the Piotroski F-Score is useful, it has limitations.

### 1. It Was Designed for Value Stocks

The original paper applied the score to high book-to-market stocks. Applying it to all stocks, especially large growth companies, may reduce its effectiveness.

### 2. It Ignores Valuation Beyond Book-to-Market

A company may have a high F-Score but still be overvalued. The F-Score measures financial strength, not whether the stock price is attractive.

### 3. It Does Not Capture Intangible Assets Well

Modern companies often rely on software, brand value, intellectual property, and network effects. Traditional accounting statements may not fully capture these assets.

### 4. It Ignores Industry Differences

A good leverage ratio or margin level can vary across industries. Banks, technology companies, manufacturers, and retailers have very different financial structures.

### 5. It Is Backward-Looking

The F-Score uses historical financial statements. Markets often price stocks based on future expectations.

### 6. It Does Not Include Momentum or Market Sentiment

Stock prices can continue rising or falling due to momentum, investor psychology, and macro trends.

### 7. It May Be Less Effective in Highly Efficient Markets

Large companies with high analyst coverage may already have their financial information priced in quickly.

---

## Future Improvements

The project can be extended in several ways:

* Apply the strategy only to high book-to-market stocks
* Increase the stock universe to S&P 500 or Russell 3000 companies
* Add book-to-market filtering
* Add sector-wise analysis
* Compare high F-Score and low F-Score portfolios
* Add benchmark comparison against S&P 500
* Add Sharpe ratio, CAGR, volatility, and max drawdown
* Add momentum and quality factors
* Add rolling backtesting
* Add statistical significance tests
* Deploy the Streamlit app online

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Piotroski_F-score
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

For macOS/Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

Create a file named `.env` in the project root.

Add:

```text
AV_API_KEY=your_alpha_vantage_api_key_here
```

### 6. Run the Streamlit app

```bash
python -m streamlit run app.py
```

---

## Disclaimer

This project is for educational and research purposes only. It is not financial advice. The F-Score should not be used as the sole basis for investment decisions.
