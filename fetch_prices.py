import yfinance as yf
import pandas as pd
import datetime
import re

# 1. ETF tickers (NSE format for Yahoo Finance)
tickers = [
    "PSUBNKBEES.NS", "GOLDBEES.NS", "LOWVOLIETF.NS", "CPSEETF.NS",
    "ICICIB22.NS", "NIFTYBEES.NS", "FMCGIETF.NS", "PVTBANIETF.NS",
    "AUTOBEES.NS", "ALPHA.NS", "HEALTHIETF.NS", "MID150BEES.NS",
    "INFRAIETF.NS", "MAKEINDIA.NS", "JUNIORBEES.NS", "PHARMABEES.NS",
    "ITBEES.NS", "TNIDETF.NS", "SILVERBEES.NS", "LTGILTBEES.NS",
    "GILT5YBEES.NS", "LIQUIDCASE.NS", "BFSI.NS", "BANKBEES.NS",
    "FINIETF.NS", "HDFCSML250.NS", "MODEFENCE.NS", "METALIETF.NS",
    "MOCAPITAL.NS"
]

# 2. Your exact date string (tab/space separated)
raw_dates = """01 June 2022	06 June 2022	13 June 2022	20 June 2022	27 June 2022	04 July 2022	11 July 2022	18 July 2022	25 July 2022	01 August 2022	08 August 2022	15 August 2022	22 August 2022	29 August 2022	05 September 2022	12 September 2022	19 September 2022	26 September 2022	03 October 2022	10 October 2022	17 October 2022	24 October 2022	31 October 2022	07 November 2022	14 November 2022	21 November 2022	28 November 2022	05 December 2022	12 December 2022	19 December 2022	26 December 2022	02 January 2023	09 January 2023	16 January 2023	23 January 2023	30 January 2023	06 February 2023	13 February 2023	20 February 2023	27 February 2023	06 March 2023	13 March 2023	20 March 2023	27 March 2023	03 April 2023	10 April 2023	17 April 2023	24 April 2023	01 May 2023	08 May 2023	15 May 2023	22 May 2023	29 May 2023	05 June 2023	12 June 2023	19 June 2023	26 June 2023	03 July 2023	10 July 2023	17 July 2023	24 July 2023	31 July 2023	07 August 2023	14 August 2023	21 August 2023	28 August 2023	04 September 2023	11 September 2023	18 September 2023	25 September 2023	02 October 2023	09 October 2023	16 October 2023	23 October 2023	30 October 2023	06 November 2023	13 November 2023	20 November 2023	27 November 2023	04 December 2023	11 December 2023	18 December 2023	25 December 2023	01 January 2024	08 January 2024	15 January 2024	22 January 2024	29 January 2024	05 February 2024	12 February 2024	19 February 2024	26 February 2024	04 March 2024	11 March 2024	18 March 2024	25 March 2024	01 April 2024	08 April 2024	15 April 2024	22 April 2024	29 April 2024	06 May 2024	13 May 2024	20 May 2024	27 May 2024	03 June 2024	10 June 2024	17 June 2024	24 June 2024	01 July 2024	08 July 2024	15 July 2024	22 July 2024	29 July 2024	05 August 2024	12 August 2024	19 August 2024	26 August 2024	02 September 2024	09 September 2024	16 September 2024	23 September 2024	30 September 2024	07 October 2024	14 October 2024	21 October 2024	28 October 2024	04 November 2024	11 November 2024	18 November 2024	25 November 2024	02 December 2024	09 December 2024	16 December 2024	23 December 2024	30 December 2024	06 January 2025	13 January 2025	20 January 2025	27 January 2025	03 February 2025	10 February 2025	17 February 2025	24 February 2025	03 March 2025	10 March 2025	17 March 2025	24 March 2025	31 March 2025	07 April 2025	14 April 2025	21 April 2025	28 April 2025	05 May 2025	12 May 2025	19 May 2025	26 May 2025	02 June 2025	09 June 2025	16 June 2025	23 June 2025	30 June 2025	07 July 2025	14 July 2025	21 July 2025	28 July 2025	04 August 2025	11 August 2025	18 August 2025	25 August 2025	01 September 2025	08 September 2025	15 September 2025	22 September 2025	29 September 2025	06 October 2025	13 October 2025	20 October 2025	27 October 2025	03 November 2025	10 November 2025	17 November 2025	24 November 2025	01 December 2025	08 December 2025	15 December 2025	22 December 2025	29 December 2025	05 January 2026	12 January 2026	19 January 2026	26 January 2026	02 February 2026	09 February 2026	16 February 2026	23 February 2026	02 March 2026	09 March 2026	16 March 2026	23 March 2026	30 March 2026	06 April 2026	13 April 2026	20 April 2026	27 April 2026	04 May 2026	11 May 2026	18 May 2026	25 May 2026	01 June 2026	08 June 2026	15 June 2026	22 June 2026	29 June 2026	06 July 2026	13 July 2026	20 July 2026	27 July 2026	30 July 2026"""

# 3. Parse & filter dates (split by tab or newline to preserve the day-month-year groups)
date_list = [d.strip() for d in re.split(r'[\t\n\r]+', raw_dates) if d.strip()]
parsed_dates = pd.to_datetime(date_list, format="%d %B %Y")
today = pd.Timestamp.today()
valid_dates = [d.strftime("%Y-%m-%d") for d in parsed_dates if d <= today]

if not valid_dates:
    print("[WARNING] No valid historical dates found. Check your date list.")
else:
    print(f"[INFO] Processing {len(valid_dates)} historical dates (future dates filtered out)...")

    # 4. Download data once (efficient)
    print("[INFO] Fetching historical data from Yahoo Finance...")
    data = yf.download(tickers, start="2022-06-01", end=today.strftime("%Y-%m-%d"), progress=False)

    # 5. Extract Close prices
    if isinstance(data.columns, pd.MultiIndex):
        close_df = data.xs('Close', level='Price', axis=1)
    else:
        close_df = data['Close']

    # 6. Filter for your exact dates & transpose (ETFs as rows, dates as columns)
    # Using reindex instead of loc to gracefully handle market holidays/weekends
    result = close_df.reindex(valid_dates).T
    result.index.name = "ETF"
    result.columns = pd.to_datetime(result.columns).strftime("%d-%b-%Y")

    # 7. Output
    print("\n[SUCCESS] Closing Prices Extracted (ETFs x Dates):")
    print(result.round(2))

    # 8. Save to CSV
    csv_path = "etf_closing_prices.csv"
    result.to_csv(csv_path)
    print(f"\n[INFO] Data saved to {csv_path}")
