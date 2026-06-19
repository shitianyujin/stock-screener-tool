# 📈 Japanese Stock Price Data Fetcher

A tool that imports any CSV containing Japanese stock ticker codes and fetches recent OHLCV data via yfinance.

## Features

- Upload any CSV where column 1 is the ticker code (4-digit) and column 2 is the stock name
- Automatically fetches OHLCV data for each ticker via yfinance
- Configurable date range (default: 180 days, recommended for MA75 calculation)
- Downloads the result as a CSV file ready for analysis

## Usage

1. Open the app URL
2. Upload a CSV file (column 1: ticker code, column 2: stock name)
3. Set the number of days to fetch (default: 180)
4. Click "株価データを取得する"
5. Download the output CSV

## Example: Using with Rakuten Securities Screener

1. Log in to [Rakuten Securities](https://www.rakuten-sec.co.jp/) and open the Stock Screener
2. Set your screening conditions and run the search
3. Click the "CSV出力" (Export CSV) button to download the results
4. Upload the downloaded CSV to this tool
5. The tool extracts ticker codes from column 1 and fetches OHLCV data for each stock

This workflow is useful for quickly gathering chart data on screener results for further technical analysis.

## Output Format

| Column | Description |
|--------|-------------|
| Code | Ticker code (4-digit) |
| Name | Stock name |
| 日付 | Date (YYYY-MM-DD) |
| 始値 | Open |
| 高値 | High |
| 安値 | Low |
| 終値 | Close |
| 出来高 | Volume |

## Input CSV Format

Any CSV file where:
- Column 1: 4-digit Japanese stock ticker code
- Column 2: Stock name

Compatible with exports from Rakuten Securities, SBI Securities, and other Japanese brokers.

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed via [Streamlit Cloud](https://share.streamlit.io).

## Disclaimer

- This tool uses [yfinance](https://github.com/ranaroussi/yfinance), an unofficial Yahoo Finance API wrapper. Data accuracy is not guaranteed.
- Data retrieval may occasionally fail due to Yahoo Finance rate limits. The tool retries up to 3 times per ticker automatically.
- This tool is for informational purposes only. All investment decisions are made at your own risk.
