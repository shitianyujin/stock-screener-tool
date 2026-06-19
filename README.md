# 📈 Rakuten Securities Screener → Stock Price Data Fetcher

A tool that imports CSV exports from Rakuten Securities screener and fetches recent stock price data for the selected tickers.

## Features

- Upload a CSV exported from Rakuten Securities screener
- Automatically extracts ticker codes and fetches OHLCV data via yfinance
- Configurable date range (default: 180 days, recommended for MA75 calculation)
- Downloads the result as a CSV file ready for analysis

## Usage

1. Open the app URL
2. Upload the CSV exported from Rakuten Securities screener
3. Set the number of days to fetch (default: 180)
4. Click "株価データを取得する"
5. Download the output CSV
6. Upload both CSVs to Claude and ask for chart analysis

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

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Deployed via [Streamlit Cloud](https://share.streamlit.io).
