import yfinance as yf
import pandas as pd
import datetime
import io
import re

# 1. ETF Tickers
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

# 2. Raw dates list from the user
raw_dates_str = """01 June 2022	06 June 2022	13 June 2022	20 June 2022	27 June 2022	04 July 2022	11 July 2022	18 July 2022	25 July 2022	01 August 2022	08 August 2022	15 August 2022	22 August 2022	29 August 2022	05 September 2022	12 September 2022	19 September 2022	26 September 2022	03 October 2022	10 October 2022	17 October 2022	24 October 2022	31 October 2022	07 November 2022	14 November 2022	21 November 2022	28 November 2022	05 December 2022	12 December 2022	19 December 2022	26 December 2022	02 January 2023	09 January 2023	16 January 2023	23 January 2023	30 January 2023	06 February 2023	13 February 2023	20 February 2023	27 February 2023	06 March 2023	13 March 2023	20 March 2023	27 March 2023	03 April 2023	10 April 2023	17 April 2023	24 April 2023	01 May 2023	08 May 2023	15 May 2023	22 May 2023	29 May 2023	05 June 2023	12 June 2023	19 June 2023	26 June 2023	03 July 2023	10 July 2023	17 July 2023	24 July 2023	31 July 2023	07 August 2023	14 August 2023	21 August 2023	28 August 2023	04 September 2023	11 September 2023	18 September 2023	25 September 2023	02 October 2023	09 October 2023	16 October 2023	23 October 2023	30 October 2023	06 November 2023	13 November 2023	20 November 2023	27 November 2023	04 December 2023	11 December 2023	18 December 2023	25 December 2023	01 January 2024	08 January 2024	15 January 2024	22 January 2024	29 January 2024	05 February 2024	12 February 2024	19 February 2024	26 February 2024	04 March 2024	11 March 2024	18 March 2024	25 March 2024	01 April 2024	08 April 2024	15 April 2024	22 April 2024	29 April 2024	06 May 2024	13 May 2024	20 May 2024	27 May 2024	03 June 2024	10 June 2024	17 June 2024	24 June 2024	01 July 2024	08 July 2024	15 July 2024	22 July 2024	29 July 2024	05 August 2024	12 August 2024	19 August 2024	26 August 2024	02 September 2024	09 September 2024	16 September 2024	23 September 2024	30 September 2024	07 October 2024	14 October 2024	21 October 2024	28 October 2024	04 November 2024	11 November 2024	18 November 2024	25 November 2024	02 December 2024	09 December 2024	16 December 2024	23 December 2024	30 December 2024	06 January 2025	13 January 2025	20 January 2025	27 January 2025	03 February 2025	10 February 2025	17 February 2025	24 February 2025	03 March 2025	10 March 2025	17 March 2025	24 March 2025	31 March 2025	07 April 2025	14 April 2025	21 April 2025	28 April 2025	05 May 2025	12 May 2025	19 May 2025	26 May 2025	02 June 2025	09 June 2025	16 June 2025	23 June 2025	30 June 2025	07 July 2025	14 July 2025	21 July 2025	28 July 2025	04 August 2025	11 August 2025	18 August 2025	25 August 2025	01 September 2025	08 September 2025	15 September 2025	22 September 2025	29 September 2025	06 October 2025	13 October 2025	20 October 2025	27 October 2025	03 November 2025	10 November 2025	17 November 2025	24 November 2025	01 December 2025	08 December 2025	15 December 2025	22 December 2025	29 December 2025	05 January 2026	12 January 2026	19 January 2026	26 January 2026	02 February 2026	09 February 2026	16 February 2026	23 February 2026	02 March 2026	09 March 2026	16 March 2026	23 March 2026	30 March 2026	06 April 2026	13 April 2026	20 April 2026	27 April 2026	04 May 2026	11 May 2026	18 May 2026	25 May 2026	01 June 2026	08 June 2026	15 June 2026	22 June 2026	29 June 2026	06 July 2026	13 July 2026	20 July 2026	27 July 2026	30 July 2026"""

# 3. Trades log from the user
trades_data = """Stock Name	Entry Price	Exit Price	Qty	P&L	Entry Date	Exit Date	Exit Reason
ALPHA	32	54.88	4039	92412.32	24 July 2023	7 October 2024	Rebalance
AUTOBEES	140.31	162.56	786	17488.5	22 May 2023	3 October 2023	Rebalance
AUTOBEES	254.15	257.95	698	2652.4	10 June 2024	21 October 2024	Rebalance
AUTOBEES	260.88	283.55	765	17342.55	25 August 2025	19 January 2026	Rebalance
BANKBEES	569.8	575.55	412	2369	26 May 2025	18 August 2025	Rebalance
BFSI	26.92	27.21	6155	1784.95	28 April 2025	25 August 2025	Rebalance
CPSEETF	35.08	45.34	2850	29241	1 June 2022	24 July 2023	Rebalance
CPSEETF	52.88	87.59	2416	83859.36	03 October 2023	18 November 2024	Rebalance
FINIETF	29.51	32.66	7974	25118.1	26 May 2025	23 February 2026	Rebalance
FMCGIETF	43.73	54.4	2468	26326.16	16 August 2022	31 July 2023	Rebalance
GILT5YBEES	59.53	62.4	3664	10515.68	24 February 2025	26 May 2025	Rebalance
GOLDBEES	43.52	43.85	2297	758.01	01 June 2022	29 August 2022	Rebalance
GOLDBEES	62.9	116.43	3364	180074.92	18 November 2024	29 June 2026	Rebalance
HDFCSML250	179.04	171.79	1350	-9787.5	30 June 2025	25 August 2025	Rebalance
HEALTHIETF	96.52	97.28	1391	1057.16	31 July 2023	16 October 2023	Rebalance
HEALTHIETF	147.53	137.75	1502	-14689.56	07 October 2024	17 February 2025	Rebalance
ICICIB22	48.42	111.34	2065	129929.8	1 June 2022	1 July 2024	Rebalance
ICICIB22	127.24	121.12	2046	-12521.52	23 February 2026	11 May 2026	Rebalance
INFRAIETF	80.92	89.95	1972	17807.16	5 February 2024	10 June 2024	Rebalance
ITBEES	44.49	40.56	4048	-15908.64	21 October 2024	3 March 2025	Rebalance
JUNIORBEES	767.87	741.01	314	-8434.04	01 July 2024	04 November 2024	Rebalance
LIQUIDCASE	107.32	108.28	1530	1468.8	3 March 2025	28 April 2025	Rebalance
LOWVOLIETF	13.47	13.98	7422	3725.84	01 June 2022	19 September 2022	Rebalance
LTGILTBEES	27.56	28.94	7509	10362.42	17 February 2025	26 May 2025	Rebalance
MAKEINDIA	148.89	153.22	1621	7018.93	1 July 2024	02 September 2024	Rebalance
METALIETF	11.65	12.81	18624	21603.85	19 January 2026	31 July 2026	EOP
MID150BEES	155.43	183.36	870	24299.1	16 October 2023	05 February 2024	Rebalance
MOCAPITAL	55.12	53.3	4495	-8180.9	11 May 2026	31 July 2026	EOP
MODEFENCE	83.3	86.58	2352	7714.56	1 September 2025	29 September 2025	Rebalance
MODEFENCE	98.62	102.33	2356	8740.76	04 May 2026	31 July 2026	EOP
NIFTYBEES	171.87	194.09	556	12354.32	13 June 2022	16 August 2022	Rebalance
PHARMABEES	23.5	22.67	10587	-8787.21	02 September 2024	16 December 2024	Rebalance
PHARMABEES	25.9	27.3	15124	21173.59	29 June 2026	31 July 2026	EOP
PSUBNKBEES	28.3	27.03	3533	-4486.91	01 June 2022	13 June 2022	Rebalance
PSUBNKBEES	32.52	81.67	3097	152217.55	29 August 2022	1 July 2024	Rebalance
PSUBNKBEES	82.53	94.14	2467	28641.87	29 September 2025	4 May 2026	Rebalance
PVTBANIETF	20.82	22.14	4982	6586.2	19 September 2022	22 May 2023	Rebalance
PVTBANIETF	27.67	28.37	8504	5952.8	26 May 2025	30 June 2025	Rebalance
SILVERBEES	87.27	94.55	2750	20020	16 December 2024	26 May 2025	Rebalance
SILVERBEES	110.06	206.4	2155	207612.69	18 August 2025	31 July 2026	EOP
TNIDETF	92.67	86.88	2511	-14538.69	4 November 2024	24 February 2025	Rebalance
TNIDETF	95.21	93.32	2097	-3963.33	25 August 2025	1 September 2025	Rebalance"""

print("[INFO] Parsing trade data and dates...")
df_trades = pd.read_csv(io.StringIO(trades_data), sep="\t")
df_trades['Entry Date'] = pd.to_datetime(df_trades['Entry Date'], format='%d %B %Y')
df_trades['Exit Date'] = pd.to_datetime(df_trades['Exit Date'], format='%d %B %Y')

# Parse raw dates list
raw_date_list = [d.strip() for d in re.split(r'[\t\n\r]+', raw_dates_str) if d.strip()]
parsed_raw_dates = pd.to_datetime(raw_date_list, format="%d %B %Y")

# Merge raw dates and trade entry/exit dates to get a 100% complete timeline
trade_dates = set(df_trades['Entry Date']).union(set(df_trades['Exit Date']))
merged_dates = set(parsed_raw_dates).union(trade_dates)

# Filter out future dates (relative to today) and sort chronologically
today = pd.Timestamp.today()
valid_dates = sorted([d for d in merged_dates if d <= today])
valid_date_strings = [d.strftime("%Y-%m-%d") for d in valid_dates]

print(f"[INFO] Timeline has {len(valid_date_strings)} unique dates (merged with all entry/exit trade dates).")

# Download historical closing prices
print("[INFO] Fetching historical data from Yahoo Finance for the complete timeline...")
# yf.download takes start and end dates. We'll use start="2022-06-01" and end=today.
data = yf.download(tickers, start="2022-06-01", end=(today + pd.Timedelta(days=1)).strftime("%Y-%m-%d"), progress=False)

# Extract Close prices
if isinstance(data.columns, pd.MultiIndex):
    close_df = data.xs('Close', level='Price', axis=1)
else:
    close_df = data['Close']

# Reindex with our complete timeline of valid dates (forward filling missing price ticks)
close_df = close_df.reindex(valid_date_strings).ffill().bfill()
close_df.index = pd.to_datetime(close_df.index)

# Save close prices to file
close_df_transposed = close_df.T
close_df_transposed.index.name = "ETF"
close_df_transposed.columns = pd.to_datetime(close_df_transposed.columns).strftime("%d-%b-%Y")
close_df_transposed.to_csv("etf_closing_prices.csv")
print("[INFO] Updated etf_closing_prices.csv saved successfully.")

# Calculate P&L for each stock over the timeline
stocks = df_trades['Stock Name'].unique()
total_pnl_df = pd.DataFrame(0.0, index=close_df.index, columns=stocks)

print("[INFO] Calculating combined (Realized + Unrealized) Total P&L over time...")
for date in close_df.index:
    for stock in stocks:
        ticker = f"{stock}.NS"
        stock_trades = df_trades[df_trades['Stock Name'] == stock]
        total_pnl_sum = 0.0
        
        for _, trade in stock_trades.iterrows():
            entry_date = trade['Entry Date']
            exit_date = trade['Exit Date']
            qty = trade['Qty']
            entry_price = trade['Entry Price']
            final_pnl = trade['P&L']
            
            # Realized P&L on or after Exit Date
            if date >= exit_date:
                total_pnl_sum += final_pnl
            # Unrealized (mark-to-market) P&L between Entry and Exit Date
            elif date >= entry_date:
                if ticker in close_df.columns:
                    current_price = close_df.loc[date, ticker]
                    if not pd.isna(current_price):
                        total_pnl_sum += qty * (current_price - entry_price)
                
        total_pnl_df.loc[date, stock] = total_pnl_sum

# Transpose the table so ETFs are rows and Dates are columns
print("[INFO] Transposing Total P&L table...")
total_pnl_df_transposed = total_pnl_df.T
total_pnl_df_transposed.index.name = "ETF"
total_pnl_df_transposed.columns = pd.to_datetime(total_pnl_df_transposed.columns).strftime('%d-%b-%Y')

# Save transposed total P&L race CSV
total_pnl_path = "total_pnl_race.csv"
total_pnl_df_transposed.round(2).to_csv(total_pnl_path)

print(f"[SUCCESS] Updated and transposed Total P&L Race table saved to {total_pnl_path}")
print("\n--- PHARMABEES Verification ---")
print(total_pnl_df_transposed.loc[['PHARMABEES'], :].iloc[:, -5:].round(2))
