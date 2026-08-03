import pandas as pd
import json
import re
import io

# 1. Load the transposed total P&L data
print("[INFO] Reading total_pnl_race.csv...")
df = pd.read_csv("total_pnl_race.csv", index_col="ETF")

# 2. Load the ETF closing prices for benchmark calculations
print("[INFO] Reading etf_closing_prices.csv...")
df_prices = pd.read_csv("etf_closing_prices.csv", index_col=0)

# Extract NIFTYBEES.NS prices for the entire timeline
nifty_prices = df_prices.loc['NIFTYBEES.NS'].to_dict()

# Extract closing prices for ALL ETFs to compute running position values dynamically in JS
prices_dict = {}
for ticker in df_prices.index:
    clean_key = ticker.replace(".NS", "")
    prices_dict[clean_key] = df_prices.loc[ticker].to_dict()

# 3. Extract dates and ETF names
dates = list(df.columns)
etfs = list(df.index)

# 4. Create the data structure for JavaScript P&L values
data_dict = {}
for d in dates:
    data_dict[d] = df[d].to_dict()

# 5. Parse the trades log to identify active positions at each timeline step
trades_data = """Stock Name	Entry Price	Exit Price	Qty	P&L	Entry Date	Exit Date	Exit Reason
PSUBNKBEES	28.3	27.03	3533	-4486.91	01 June 2022	13 June 2022	Rebalance
NIFTYBEES	171.87	194.09	556	12354.32	13 June 2022	16 August 2022	Rebalance
GOLDBEES	43.52	43.85	2297	758.01	01 June 2022	29 August 2022	Rebalance
LOWVOLIETF	13.47	13.98	7422	3725.84	01 June 2022	19 September 2022	Rebalance
PVTBANIETF	20.82	22.14	4982	6586.2	19 September 2022	22 May 2023	Rebalance
CPSEETF	35.08	45.34	2850	29241.0	01 June 2022	24 July 2023	Rebalance
FMCGIETF	43.73	54.4	2468	26326.16	16 August 2022	31 July 2023	Rebalance
AUTOBEES	140.31	162.56	786	17488.5	22 May 2023	03 October 2023	Rebalance
HEALTHIETF	96.52	97.28	1391	1057.16	31 July 2023	16 October 2023	Rebalance
MID150BEES	155.43	183.36	870	24299.1	16 October 2023	05 February 2024	Rebalance
INFRAIETF	80.92	89.95	1972	17807.16	05 February 2024	10 June 2024	Rebalance
ICICIB22	48.42	111.34	2065	129929.8	01 June 2022	01 July 2024	Rebalance
PSUBNKBEES	32.52	81.67	3097	152217.55	29 August 2022	01 July 2024	Rebalance
MAKEINDIA	148.89	153.22	1621	7018.93	01 July 2024	02 September 2024	Rebalance
ALPHA	32.0	54.88	4039	92412.32	24 July 2023	07 October 2024	Rebalance
AUTOBEES	254.15	257.95	698	2652.4	10 June 2024	21 October 2024	Rebalance
JUNIORBEES	767.87	741.01	314	-8434.04	01 July 2024	04 November 2024	Rebalance
CPSEETF	52.88	87.59	2416	83859.36	03 October 2023	18 November 2024	Rebalance
PHARMABEES	23.5	22.67	10587	-8787.21	02 September 2024	16 December 2024	Rebalance
HEALTHIETF	147.53	137.75	1502	-14689.56	07 October 2024	17 February 2025	Rebalance
TNIDETF	92.67	86.88	2511	-14538.69	04 November 2024	24 February 2025	Rebalance
ITBEES	44.49	40.56	4048	-15908.64	21 October 2024	03 March 2025	Rebalance
LIQUIDCASE	107.32	108.28	1530	1468.8	03 March 2025	28 April 2025	Rebalance
SILVERBEES	87.27	94.55	2750	20020.0	16 December 2024	26 May 2025	Rebalance
LTGILTBEES	27.56	28.94	7509	10362.42	17 February 2025	26 May 2025	Rebalance
GILT5YBEES	59.53	62.4	3664	10515.68	24 February 2025	26 May 2025	Rebalance
PVTBANIETF	27.67	28.37	8504	5952.8	26 May 2025	30 June 2025	Rebalance
BANKBEES	569.8	575.55	412	2369.0	26 May 2025	18 August 2025	Rebalance
BFSI	26.92	27.21	6155	1784.95	28 April 2025	25 August 2025	Rebalance
HDFCSML250	179.04	171.79	1350	-9787.5	30 June 2025	25 August 2025	Rebalance
TNIDETF	95.21	93.32	2097	-3963.33	25 August 2025	01 September 2025	Rebalance
MODEFENCE	83.3	86.58	2352	7714.56	01 September 2025	29 September 2025	Rebalance
AUTOBEES	260.88	283.55	765	17342.55	25 August 2025	19 January 2026	Rebalance
FINIETF	29.51	32.66	7974	25118.1	26 May 2025	23 February 2026	Rebalance
PSUBNKBEES	82.53	94.14	2467	28641.87	29 September 2025	04 May 2026	Rebalance
ICICIB22	127.24	121.12	2046	-12521.52	23 February 2026	11 May 2026	Rebalance
GOLDBEES	62.9	116.43	3364	180074.92	18 November 2024	29 June 2026	Rebalance
SILVERBEES	110.06	206.5	2155	207828.2	18 August 2025	03 August 2026	EOP
METALIETF	11.65	12.99	18624	24956.16	19 January 2026	03 August 2026	EOP
MODEFENCE	98.62	102.24	2356	8528.71	04 May 2026	03 August 2026	EOP
MOCAPITAL	55.12	52.9	4495	-9978.89	11 May 2026	03 August 2026	EOP
PHARMABEES	25.9	27.34	15124	21778.56	29 June 2026	03 August 2026	EOP"""

df_trades = pd.read_csv(io.StringIO(trades_data), sep="\t")
df_trades['Entry Date'] = pd.to_datetime(df_trades['Entry Date'], format='%d %B %Y')
df_trades['Exit Date'] = pd.to_datetime(df_trades['Exit Date'], format='%d %B %Y')

# Map each timeline date to the list of active stock positions on that date
active_trades_dict = {}
for d_str in dates:
    d = pd.to_datetime(d_str, format="%d-%b-%Y")
    active_stocks = []
    for _, trade in df_trades.iterrows():
        if trade['Entry Date'] <= d < trade['Exit Date']:
            active_stocks.append(trade['Stock Name'])
    active_trades_dict[d_str] = active_stocks

# Parse the spreadsheet's own total P&L timeline from ExitTrades (4).csv
timeline_pnl = {}
with open("ExitTrades (4).csv", "r", encoding="utf-8") as f:
    lines = f.readlines()

timeline_start_idx = -1
for i, line in enumerate(lines):
    if "Unrealised PL" in line and "Realised PL" in line:
        timeline_start_idx = i
        break

if timeline_start_idx != -1:
    timeline_lines = [lines[timeline_start_idx]]
    for line in lines[timeline_start_idx + 1:]:
        line_str = line.strip().lower()
        if "performance" in line_str or "total p&l" in line_str or not line.strip():
            break
        timeline_lines.append(line)
        
    csv_data = "".join(timeline_lines)
    df_time = pd.read_csv(io.StringIO(csv_data))
    df_time = df_time.dropna(subset=['Date'])
    df_time['Date'] = df_time['Date'].apply(lambda x: re.sub(r'\(.*?\)', '', str(x)).strip())
    df_time['ParsedDate'] = pd.to_datetime(df_time['Date'], format='%d %B %Y').dt.strftime('%d-%b-%Y')
    
    # Reindex series to match the full dates array (with forward filling)
    time_series = df_time.set_index('ParsedDate')['Total PL']
    all_dates_index = pd.Index(dates, name='ParsedDate')
    # Combine and forward fill to cover any trade-date points not explicitly in the timeline table
    time_series_reindexed = time_series.reindex(all_dates_index).ffill().bfill()
    timeline_pnl = time_series_reindexed.to_dict()

# Serialize trades details for JS tables
trades_list = []
for _, row in df_trades.iterrows():
    trades_list.append({
        "stock": row["Stock Name"],
        "entryPrice": float(row["Entry Price"]),
        "exitPrice": float(row["Exit Price"]),
        "qty": int(row["Qty"]),
        "pnl": float(row["P&L"]),
        "entryDate": row["Entry Date"].strftime("%d-%b-%Y"),
        "exitDate": row["Exit Date"].strftime("%d-%b-%Y"),
        "exitReason": row["Exit Reason"]
    })

# Calculate global maximum absolute value for scaling
global_max = float(df.max().max())
global_min = float(df.min().min())
abs_max_scale = max(abs(global_max), abs(global_min))

# Convert variables to JSON
dates_json = json.dumps(dates)
etfs_json = json.dumps(etfs)
data_json = json.dumps(data_dict)
active_trades_json = json.dumps(active_trades_dict)
nifty_prices_json = json.dumps(nifty_prices)
prices_json = json.dumps(prices_dict)
trades_json = json.dumps(trades_list)
excel_total_pnl_json = json.dumps(timeline_pnl)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentify ETF Strategy</title>
    
    <!-- Import Outfit font from Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-color: #0b0f19;
            --panel-bg: #151c2c;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.35);
            --green: #10b981;
            --red: #ef4444;
            --grid-line: rgba(255, 255, 255, 0.05);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            padding: 1.5rem;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}

        .app-layout {{
            width: 100%;
            max-width: 1600px; /* Expanded to allow space for three columns */
            height: calc(100vh - 3rem);
            display: flex;
            gap: 1.25rem;
        }}

        /* Column 1: Sidebar (Left) Controls & Ratios */
        .sidebar {{
            width: 290px;
            flex-shrink: 0;
            background-color: var(--panel-bg);
            border-radius: 16px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
            overflow-y: auto;
        }}

        .title-area h1 {{
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.15;
            background: linear-gradient(135deg, #60a5fa, #3b82f6, #1d4ed8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
        }}

        .title-area p {{
            color: var(--text-muted);
            font-size: 0.78rem;
            margin-top: 0.3rem;
            line-height: 1.4;
        }}

        /* Stats Panel */
        .stats-panel {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            background-color: rgba(0, 0, 0, 0.15);
            padding: 0.85rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}

        .stat-box {{
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }}

        .stat-label {{
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .stat-value {{
            font-size: 1.2rem;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }}

        #date-display {{
            color: #60a5fa;
            text-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
        }}

        /* Controls Block */
        .controls-block {{
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }}

        .button-group {{
            display: flex;
            gap: 0.5rem;
        }}

        button {{
            flex: 1;
            background-color: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            padding: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-family: inherit;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.3rem;
            transition: all 0.2s ease;
            font-size: 0.8rem;
        }}

        button:hover {{
            background-color: var(--accent);
            border-color: var(--accent);
            box-shadow: 0 0 12px var(--accent-glow);
        }}

        button:active {{
            transform: scale(0.97);
        }}

        .control-item {{
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }}

        .control-item label {{
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }}

        select, input[type="range"] {{
            background-color: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-main);
            padding: 0.4rem 0.5rem;
            border-radius: 6px;
            font-family: inherit;
            font-weight: 500;
            outline: none;
            cursor: pointer;
            font-size: 0.8rem;
            width: 100%;
        }}

        select:focus {{
            border-color: var(--accent);
        }}

        input[type="range"] {{
            height: 6px;
            -webkit-appearance: none;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 3px;
        }}

        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: var(--accent);
            cursor: pointer;
            box-shadow: 0 0 5px var(--accent-glow);
        }}

        /* Strategy Ratios Panel inside Left Sidebar */
        .ratios-panel {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 0.85rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .ratios-panel-title {{
            font-size: 0.75rem;
            font-weight: 700;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.35rem;
        }}

        .ratios-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem 0.5rem;
        }}

        .ratio-item {{
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }}

        .ratio-lbl {{
            font-size: 0.62rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            line-height: 1.2;
        }}

        .ratio-val {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-main);
            font-variant-numeric: tabular-nums;
        }}

        .ratio-val.green {{
            color: var(--green);
        }}

        .ratio-val.blue {{
            color: #60a5fa;
        }}

        /* Column 2: Middle Bar Chart Race Column */
        .middle-column {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            height: 100%;
            overflow: hidden;
        }}

        /* Timeline Scrubber inside Middle Column */
        .scrubber-container {{
            display: flex;
            align-items: center;
            gap: 1rem;
            background-color: var(--panel-bg);
            padding: 0.75rem 1.25rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            flex-shrink: 0;
        }}

        #timeline-scrubber {{
            flex-grow: 1;
        }}

        /* Chart Wrapper in Middle Column */
        .chart-wrapper {{
            background-color: var(--panel-bg);
            border-radius: 16px;
            padding: 1.75rem 2.25rem 2.25rem 2.25rem;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            flex-grow: 1; 
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }}

        .chart-area {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: height 0.4s ease;
        }}

        /* Grid lines in background */
        .grid-lines {{
            position: absolute;
            top: 0;
            bottom: 0;
            left: 180px; /* updated dynamically */
            right: 140px;  /* updated dynamically */
            pointer-events: none;
            display: flex;
            justify-content: space-between;
            z-index: 1;
            transition: left 0.4s ease, right 0.4s ease;
        }}

        .grid-line {{
            width: 1px;
            height: 100%;
            background-color: var(--grid-line);
            position: relative;
        }}

        .grid-label {{
            position: absolute;
            bottom: -22px;
            transform: translateX(-50%);
            font-size: 0.7rem;
            color: var(--text-muted);
            font-weight: 500;
            white-space: nowrap;
        }}

        /* Individual Bar rows */
        .bar-row {{
            position: absolute;
            left: 0;
            height: 38px;
            width: 100%;
            display: flex;
            align-items: center;
            z-index: 2;
        }}

        /* Active Holdings Styling */
        .bar-row.active {{
            opacity: 1.0;
        }}

        .bar-row.inactive {{
            opacity: 0.35;
        }}

        .active-indicator {{
            width: 6px;
            height: 6px;
            background-color: var(--green);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--green);
            margin-left: 4px;
            animation: pulse 1.5s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(0.9); opacity: 0.6; }}
            50% {{ transform: scale(1.25); opacity: 1; }}
            100% {{ transform: scale(0.9); opacity: 0.6; }}
        }}

        .bar-label {{
            width: 160px; /* updated dynamically */
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-right: 12px;
            text-align: right;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.4rem;
            transition: transform 0.2s ease, color 0.2s ease, width 0.4s ease, font-size 0.4s ease;
        }}

        .bar-track {{
            flex-grow: 1;
            height: 100%;
            display: flex;
            align-items: center;
            position: relative;
        }}

        .bar-fill {{
            height: 20px; /* updated dynamically */
            border-radius: 4px;
            position: absolute;
            top: auto;
            left: 0;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }}

        /* Hover effects */
        .bar-row:hover .bar-fill {{
            filter: brightness(1.2);
            transform: scaleY(1.08);
            cursor: pointer;
        }}
        
        .bar-row:hover .bar-label {{
            transform: translateX(3px);
            color: #ffffff;
        }}

        .bar-value {{
            width: 120px; /* updated dynamically */
            font-size: 0.82rem;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            padding-left: 12px;
            text-align: left;
            transition: color 0.2s ease, font-size 0.4s ease, width 0.4s ease;
            overflow: hidden;
            text-overflow: clip;
            white-space: nowrap;
        }}

        .bar-value.positive {{
            color: var(--green);
        }}

        .bar-value.negative {{
            color: var(--red);
        }}

        /* Invested Capital summary panel */
        .bottom-stats-panel {{
            background-color: var(--panel-bg);
            border-radius: 12px;
            padding: 0.85rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            gap: 1.25rem;
            flex-shrink: 0;
        }}

        .bottom-stat-box {{
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
            flex: 1;
            align-items: center;
            min-width: 0; /* allows shrinking text inside */
        }}

        .bottom-stat-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            font-weight: 600;
            white-space: nowrap;
        }}

        .bottom-stat-value-neutral {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--text-main);
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }}

        .bottom-stat-value {{
            font-size: 1.35rem;
            font-weight: 800;
            font-variant-numeric: tabular-nums;
            transition: color 0.2s ease, font-size 0.2s ease;
            white-space: nowrap;
        }}

        .stat-divider {{
            width: 1px;
            height: 30px;
            background-color: rgba(255, 255, 255, 0.1);
            flex-shrink: 0;
        }}

        .bottom-stat-value.positive {{
            color: var(--green);
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
        }}

        .bottom-stat-value.negative {{
            color: var(--red);
            text-shadow: 0 0 10px rgba(239, 68, 68, 0.25);
        }}

        /* Column 3: Details & Simulator tables Column (Right) */
        .right-column {{
            width: 440px;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            height: 100%;
            overflow: hidden;
        }}

        /* Benchmark Card inside Right Column */
        .benchmark-panel {{
            background-color: rgba(0, 0, 0, 0.2);
            border: 1px dashed rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex-shrink: 0;
        }}

        .benchmark-header {{
            display: flex;
            flex-direction: column;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.4rem;
        }}

        .benchmark-title {{
            font-size: 0.78rem;
            font-weight: 800;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        .benchmark-subtitle {{
            font-size: 0.65rem;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .benchmark-content {{
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }}

        .benchmark-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
        }}

        .benchmark-label {{
            color: var(--text-muted);
            font-weight: 500;
        }}

        .benchmark-val {{
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            color: var(--text-main);
            transition: font-size 0.2s ease;
        }}

        .benchmark-val.positive {{
            color: var(--green);
        }}

        .benchmark-val.negative {{
            color: var(--red);
        }}

        /* Simulator Activity panels inside Right Column */
        .sim-panel {{
            background-color: var(--panel-bg);
            border-radius: 12px;
            padding: 0.85rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            min-height: 0; /* Ensures flex container can shrink properly */
        }}

        .sim-panel-title {{
            font-size: 0.78rem;
            font-weight: 700;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.35rem;
            flex-shrink: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .table-container {{
            flex-grow: 1;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.72rem;
            text-align: left;
        }}

        th {{
            position: sticky;
            top: 0;
            background-color: var(--panel-bg);
            color: var(--text-muted);
            font-weight: 600;
            padding: 0.35rem;
            font-size: 0.65rem;
            text-transform: uppercase;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 10;
        }}

        td {{
            padding: 0.3rem 0.35rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            font-variant-numeric: tabular-nums;
        }}

        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.02);
        }}

        .text-green {{
            color: var(--green) !important;
            font-weight: 600;
        }}

        .text-red {{
            color: var(--red) !important;
            font-weight: 600;
        }}

        .empty-row-msg {{
            color: var(--text-muted);
            text-align: center;
            padding: 1rem;
            font-style: italic;
            font-size: 0.72rem;
        }}

        /* Responsive Layout Rules */
        @media (max-width: 1100px) {{
            body {{
                overflow-y: auto;
                height: auto;
                padding: 1rem;
            }}
            .app-layout {{
                flex-direction: column;
                height: auto;
                gap: 1.25rem;
            }}
            .sidebar {{
                width: 100%;
                height: auto;
                overflow-y: visible;
            }}
            .middle-column {{
                height: 500px;
                flex-grow: 0;
            }}
            .right-column {{
                width: 100%;
                height: auto;
                overflow-y: visible;
                gap: 1.25rem;
            }}
            .sim-panel {{
                height: 250px;
            }}
        }}

        .hidden {{
            display: none !important;
        }}

        svg {{
            width: 16px;
            height: 16px;
            fill: currentColor;
        }}
    </style>
</head>
<body>

<div class="app-layout">
    <!-- Column 1: Sidebar Controls (Left) -->
    <aside class="sidebar">
        <div class="title-area">
            <h1>Momentify<br>ETF Strategy</h1>
            <p>Interactive timeline tracking cumulative realized & unrealized performance</p>
        </div>
        
        <div class="stats-panel">
            <div class="stat-box">
                <div class="stat-label">Start Date</div>
                <div class="stat-value" id="start-date-display" style="color: var(--text-main); font-size: 1.2rem;">--/--/----</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">End Date</div>
                <div class="stat-value" id="date-display" style="font-size: 1.2rem;">--/--/----</div>
            </div>
        </div>

        <div class="controls-block">
            <div class="button-group">
                <button id="play-btn">
                    <svg id="play-icon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                    <svg id="pause-icon" class="hidden" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                    <span id="play-text">Play</span>
                </button>
                <button id="reset-btn">
                    <svg viewBox="0 0 24 24"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>
                    <span>Reset</span>
                </button>
            </div>

            <div class="control-item">
                <label for="speed-range">Animation Speed</label>
                <input type="range" id="speed-range" min="100" max="1000" step="50" value="400">
            </div>

            <div class="control-item">
                <label for="limit-select">Show Top</label>
                <select id="limit-select">
                    <option value="10">Top 10 ETFs</option>
                    <option value="15">Top 15 ETFs</option>
                    <option value="20">Top 20 ETFs</option>
                    <option value="29" selected>Show All (29)</option>
                </select>
            </div>
        </div>

        <!-- Strategy Backtest Ratios Panel -->
        <div class="ratios-panel">
            <div class="ratios-panel-title">Strategy Ratios</div>
            <div class="ratios-grid">
                <div class="ratio-item">
                    <span class="ratio-lbl">Total Trades</span>
                    <span class="ratio-val blue">42</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Win Rate</span>
                    <span class="ratio-val green">73.81%</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Sharpe Ratio</span>
                    <span class="ratio-val blue">1.21</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Sortino Ratio</span>
                    <span class="ratio-val blue">23.33</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Monthly Return</span>
                    <span class="ratio-val green">3.76%</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Monthly Churn</span>
                    <span class="ratio-val">0.75</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Positive Months</span>
                    <span class="ratio-val green">67.86%</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Positive Years</span>
                    <span class="ratio-val green">100%</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Avg Annual Return</span>
                    <span class="ratio-val green">41.86%</span>
                </div>
                <div class="ratio-item">
                    <span class="ratio-lbl">Median Annual</span>
                    <span class="ratio-val green">46.54%</span>
                </div>
                <div class="ratio-item" style="grid-column: span 2;">
                    <div style="display:flex; justify-content:space-between; border-top:1px solid rgba(255,255,255,0.05); padding-top:0.4rem; margin-top:0.2rem;">
                        <div class="ratio-item">
                            <span class="ratio-lbl">Avg Pos Year</span>
                            <span class="ratio-val green">41.86%</span>
                        </div>
                        <div class="ratio-item">
                            <span class="ratio-lbl">Avg Neg Year</span>
                            <span class="ratio-val text-red">0.00%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Column 2: Bar Chart Race (Middle) -->
    <main class="middle-column">
        <!-- Total P&L summary - shifted ABOVE the chart -->
        <div class="bottom-stats-panel">
            <div class="bottom-stat-box">
                <span class="bottom-stat-label">Invested Capital</span>
                <span class="bottom-stat-value-neutral">₹5,00,000.00</span>
            </div>
            <div class="stat-divider"></div>
            <div class="bottom-stat-box">
                <span class="bottom-stat-label">Total Portfolio P&L</span>
                <span class="bottom-stat-value" id="total-pnl-display">₹0.00</span>
            </div>
            <div class="stat-divider"></div>
            <div class="bottom-stat-box">
                <span class="bottom-stat-label">Absolute Return</span>
                <span class="bottom-stat-value" id="portfolio-pct-display">0.00%</span>
            </div>
            <div class="stat-divider"></div>
            <div class="bottom-stat-box">
                <span class="bottom-stat-label">System CAGR</span>
                <span class="bottom-stat-value" id="portfolio-cagr-display">0.00% p.a.</span>
            </div>
            <div class="stat-divider"></div>
            <div class="bottom-stat-box">
                <span class="bottom-stat-label">Max Drawdown</span>
                <span class="bottom-stat-value" id="portfolio-maxdd-display" style="color: var(--red);">0.00%</span>
            </div>
        </div>

        <!-- Chart Canvas - takes maximum vertical space -->
        <div class="chart-wrapper">
            <div class="chart-area" id="chart-container">
                <div class="grid-lines" id="grid-lines-container">
                    <!-- Grid lines injected via JS -->
                </div>
                <!-- Bars injected and updated via JS -->
            </div>
        </div>

        <!-- Timeline Scrubber - shifted BELOW the chart -->
        <div class="scrubber-container">
            <span id="start-date-lbl" style="font-size: 0.75rem; color: var(--text-muted); font-weight:600;">Start</span>
            <input type="range" id="timeline-scrubber" min="0" max="0" value="0">
            <span id="end-date-lbl" style="font-size: 0.75rem; color: var(--text-muted); font-weight:600;">End</span>
        </div>
    </main>

    <!-- Column 3: Rest of Details (Right) -->
    <aside class="right-column">
        <!-- Benchmark Card -->
        <div class="benchmark-panel">
            <div class="benchmark-header">
                <span class="benchmark-title">NIFTYBEES Buy & Hold</span>
                <span class="benchmark-subtitle">Alternative 5L Investment</span>
            </div>
            <div class="benchmark-content">
                <div class="benchmark-row">
                    <span class="benchmark-label">Value:</span>
                    <span class="benchmark-val" id="nifty-val-display">₹5,00,000.00</span>
                </div>
                <div class="benchmark-row">
                    <span class="benchmark-label">P&L:</span>
                    <span class="benchmark-val" id="nifty-pnl-display">₹0.00</span>
                </div>
                <div class="benchmark-row">
                    <span class="benchmark-label">Return:</span>
                    <span class="benchmark-val" id="nifty-pct-display">0.00%</span>
                </div>
                <div class="benchmark-row">
                    <span class="benchmark-label">CAGR:</span>
                    <span class="benchmark-val" id="nifty-cagr-display">0.00% p.a.</span>
                </div>
                <div class="benchmark-row">
                    <span class="benchmark-label">Max Drawdown:</span>
                    <span class="benchmark-val" id="nifty-maxdd-display" style="color: var(--red);">0.00%</span>
                </div>
            </div>
        </div>

        <!-- Running Stocks Panel (Scrollable) -->
        <div class="sim-panel" style="flex: 2;">
            <div class="sim-panel-title">Running Stocks (Open Positions)</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Entry Price</th>
                            <th>Qty</th>
                            <th>Current Price</th>
                            <th>P&L</th>
                            <th>Return</th>
                        </tr>
                    </thead>
                    <tbody id="running-body">
                        <!-- Injected via JS -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Exited Stocks Panel (Scrollable) -->
        <div class="sim-panel" style="flex: 1.2;">
            <div class="sim-panel-title" id="exited-title">Exited Stocks (as of --/--/----)</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Entry</th>
                            <th>Exit</th>
                            <th>Qty</th>
                            <th>P&L</th>
                            <th>Return</th>
                        </tr>
                    </thead>
                    <tbody id="exited-body">
                        <!-- Injected via JS -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Added Stocks Panel (Scrollable) -->
        <div class="sim-panel" style="flex: 1.2;">
            <div class="sim-panel-title" id="added-title">Added Stocks (as of --/--/----)</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Entry Price</th>
                            <th>Qty</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody id="added-body">
                        <!-- Injected via JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </aside>
</div>

<script>
    // Embedded Data
    const dates = {dates_json};
    const etfs = {etfs_json};
    const dataset = {data_json};
    const activeTrades = {active_trades_json};
    const niftyPrices = {nifty_prices_json};
    const prices = {prices_json};
    const tradesList = {trades_json};
    const excelTotalPnl = {excel_total_pnl_json};
    const globalMaxAbs = {abs_max_scale};

    // App State
    let currentIndex = 0;
    let isPlaying = false;
    let timer = null;
    let speed = 400; 
    let topN = 29; // show all
    const scaleMode = 'absolute'; // locked to global max as default

    // Colors mapping (strictly Green-based for positive, Red-based for negative)
    const colorMap = {{}};
    etfs.forEach(etf => {{
        let hash = 0;
        for (let i = 0; i < etf.length; i++) {{
            hash = etf.charCodeAt(i) + ((hash << 5) - hash);
        }}
        const greenHue = 120 + Math.abs(hash % 40);
        const redHue = (345 + Math.abs(hash % 20)) % 360;

        colorMap[etf] = {{
            greenBase: `hsl(${{greenHue}}, 70%, 42%)`,
            greenLight: `hsl(${{greenHue}}, 80%, 56%)`,
            greenGlow: `rgba(16, 185, 129, 0.35)`,
            redBase: `hsl(${{redHue}}, 70%, 42%)`,
            redLight: `hsl(${{redHue}}, 80%, 56%)`,
            redGlow: `rgba(239, 68, 68, 0.35)`
        }};
    }});

    // DOM Elements
    const playBtn = document.getElementById('play-btn');
    const playText = document.getElementById('play-text');
    const playIcon = document.getElementById('play-icon');
    const pauseIcon = document.getElementById('pause-icon');
    const resetBtn = document.getElementById('reset-btn');
    const speedRange = document.getElementById('speed-range');
    const limitSelect = document.getElementById('limit-select');
    const timelineScrubber = document.getElementById('timeline-scrubber');
    const dateDisplay = document.getElementById('date-display');
    const totalPnlDisplay = document.getElementById('total-pnl-display');
    const portfolioPctDisplay = document.getElementById('portfolio-pct-display');
    const portfolioCagrDisplay = document.getElementById('portfolio-cagr-display');
    const portfolioMaxDdDisplay = document.getElementById('portfolio-maxdd-display');
    const chartContainer = document.getElementById('chart-container');
    const gridContainer = document.getElementById('grid-lines-container');
    const startDateLbl = document.getElementById('start-date-lbl');
    const endDateLbl = document.getElementById('end-date-lbl');

    // Nifty Benchmark DOM
    const niftyValDisplay = document.getElementById('nifty-val-display');
    const niftyPnlDisplay = document.getElementById('nifty-pnl-display');
    const niftyPctDisplay = document.getElementById('nifty-pct-display');
    const niftyCagrDisplay = document.getElementById('nifty-cagr-display');
    const niftyMaxDdDisplay = document.getElementById('nifty-maxdd-display');

    // Simulator Tables DOM
    const runningBody = document.getElementById('running-body');
    const exitedBody = document.getElementById('exited-body');
    const addedBody = document.getElementById('added-body');
    const exitedTitle = document.getElementById('exited-title');
    const addedTitle = document.getElementById('added-title');

    // Initialize App
    function init() {{
        timelineScrubber.max = dates.length - 1;
        startDateLbl.textContent = dates[0];
        endDateLbl.textContent = dates[dates.length - 1];
        document.getElementById('start-date-display').textContent = dates[0];

        createBarElements();
        updateFrame();

        playBtn.addEventListener('click', togglePlay);
        resetBtn.addEventListener('click', resetChart);
        speedRange.addEventListener('input', updateSpeed);
        limitSelect.addEventListener('change', updateLimit);
        timelineScrubber.addEventListener('input', scrubTimeline);

        window.addEventListener('resize', () => {{
            updateFrame();
        }});
    }}

    function createBarElements() {{
        const gridHtml = gridContainer.outerHTML;
        chartContainer.innerHTML = gridHtml;
        const gridContainer_ref = document.getElementById('grid-lines-container');

        etfs.forEach(etf => {{
            const row = document.createElement('div');
            row.className = 'bar-row';
            row.id = `row-${{etf}}`;
            row.style.top = '1200px';

            const label = document.createElement('div');
            label.className = 'bar-label';
            label.id = `lbl-${{etf}}`;
            label.innerHTML = `<span style="font-weight:600;">${{etf}}</span>`;

            const track = document.createElement('div');
            track.className = 'bar-track';

            const fill = document.createElement('div');
            fill.className = 'bar-fill positive';
            fill.id = `fill-${{etf}}`;
            fill.style.width = '0%';
            fill.style.backgroundColor = colorMap[etf].greenBase;
            fill.style.boxShadow = `0 0 10px ${{colorMap[etf].greenGlow}}`;

            track.appendChild(fill);

            const value = document.createElement('div');
            value.className = 'bar-value';
            value.id = `val-${{etf}}`;
            value.textContent = '₹0.00';

            row.appendChild(label);
            row.appendChild(track);
            row.appendChild(value);
            chartContainer.appendChild(row);
        }});
    }}

    // Text shrink helper to adapt font size to container boundaries
    function setAdaptiveFontRem(element, text, baseRem) {{
        element.textContent = text;
        if (text.length > 15) {{
            element.style.fontSize = (baseRem * 0.72) + 'rem';
        }} else if (text.length > 12) {{
            element.style.fontSize = (baseRem * 0.84) + 'rem';
        }} else {{
            element.style.fontSize = baseRem + 'rem';
        }}
    }}

    function updateFrame() {{
        const currentDate = dates[currentIndex];
        dateDisplay.textContent = currentDate;
        timelineScrubber.value = currentIndex;

        // Dynamic Title updates: display the active date variable dynamically
        exitedTitle.textContent = `Exited Stocks (as of ${{currentDate}})`;
        addedTitle.textContent = `Added Stocks (as of ${{currentDate}})`;

        const dateData = dataset[currentDate];
        const activeList = activeTrades[currentDate] || [];

        // Dynamic adaptivity calculations based on actual viewport space
        const containerWidth = chartContainer.clientWidth;
        const containerHeight = chartContainer.clientHeight || 500; 

        // Calculate dynamic label and value column widths based on available width
        let labelWidth = 140;
        let valueWidth = 115;
        if (containerWidth < 700) {{
            labelWidth = 90;
            valueWidth = 90;
        }} else if (containerWidth > 1100) {{
            labelWidth = 160;
            valueWidth = 125;
        }}

        // Calculate dynamic row sizing to fit available vertical height exactly
        const rowOffset = containerHeight / topN;
        const rowHeight = Math.max(8, rowOffset - 3);
        const barHeight = Math.min(28, Math.max(5, rowHeight * 0.65));

        // Calculate dynamic font scaling (capped for visual balance)
        const fontSize = Math.min(16, Math.max(9, rowHeight * 0.55)) + 'px';

        const gridContainer_ref = document.getElementById('grid-lines-container');
        gridContainer_ref.style.left = `${{labelWidth}}px`;
        gridContainer_ref.style.right = `${{valueWidth}}px`;

        // Calculate time delta in years for CAGR calculation
        const startDate = new Date(dates[0].replace(/-/g, ' '));
        const currentDateObj = new Date(currentDate.replace(/-/g, ' '));
        const diffTime = Math.abs(currentDateObj - startDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const diffYears = diffDays / 365.25;

        // Fetch total portfolio P&L directly from Excel's dynamic timeline P&L mapping
        const totalPnl = excelTotalPnl[currentDate] !== undefined ? excelTotalPnl[currentDate] : 0.0;

        // Format and set adaptive text for Bottom Stats
        const formattedTotal = formatCurrency(totalPnl);
        setAdaptiveFontRem(totalPnlDisplay, formattedTotal, 1.35);
        if (totalPnl >= 0) {{
            totalPnlDisplay.className = 'bottom-stat-value positive';
        }} else {{
            totalPnlDisplay.className = 'bottom-stat-value negative';
        }}

        const portfolioPct = (totalPnl / 500000.0) * 100;
        const pctText = (portfolioPct >= 0 ? '+' : '') + portfolioPct.toFixed(2) + '%';
        setAdaptiveFontRem(portfolioPctDisplay, pctText, 1.35);
        portfolioPctDisplay.className = 'bottom-stat-value ' + (portfolioPct >= 0 ? 'positive' : 'negative');

        let portfolioCagr = 'N/A';
        if (diffYears >= 0.1) {{
            const cagrVal = (Math.pow(1 + (totalPnl / 500000.0), 1 / diffYears) - 1) * 100;
            portfolioCagr = cagrVal.toFixed(2) + '% p.a.';
            setAdaptiveFontRem(portfolioCagrDisplay, portfolioCagr, 1.35);
            portfolioCagrDisplay.className = 'bottom-stat-value ' + (portfolioPct >= 0 ? 'positive' : 'negative');
        }} else {{
            portfolioCagrDisplay.textContent = 'N/A';
            portfolioCagrDisplay.style.fontSize = '1.35rem';
            portfolioCagrDisplay.className = 'bottom-stat-value';
        }}

        // Dynamic Max Drawdown Calculation based strictly on Excel portfolio timeline values
        let peakValue = 500000.0;
        let maxDrawdown = 0.0;
        for (let i = 0; i <= currentIndex; i++) {{
            const date = dates[i];
            const stepPnl = excelTotalPnl[date] !== undefined ? excelTotalPnl[date] : 0.0;
            const portfolioValue = 500000.0 + stepPnl;
            if (portfolioValue > peakValue) {{
                peakValue = portfolioValue;
            }}
            const dd = ((peakValue - portfolioValue) / peakValue) * 100.0;
            if (dd > maxDrawdown) {{
                maxDrawdown = dd;
            }}
        }}
        const maxDdText = '-' + maxDrawdown.toFixed(2) + '%';
        setAdaptiveFontRem(portfolioMaxDdDisplay, maxDdText, 1.35);

        // Calculate NIFTYBEES Buy & Hold Alternative
        const niftyStartPrice = niftyPrices[dates[0]];
        const niftyCurrentPrice = niftyPrices[currentDate];
        let niftyVal = 500000.0;
        let niftyPnl = 0.0;
        let niftyPct = 0.0;
        let niftyCagr = 'N/A';

        if (niftyStartPrice && niftyCurrentPrice) {{
            const priceRatio = niftyCurrentPrice / niftyStartPrice;
            niftyVal = 500000.0 * priceRatio;
            niftyPnl = niftyVal - 500000.0;
            niftyPct = (priceRatio - 1.0) * 100;

            if (diffYears >= 0.1) {{
                const niftyCagrVal = (Math.pow(priceRatio, 1 / diffYears) - 1) * 100;
                niftyCagr = niftyCagrVal.toFixed(2) + '% p.a.';
            }}
        }}

        // NIFTY Dynamic Max Drawdown Calculation
        let niftyPeak = 500000.0;
        let niftyMaxDD = 0.0;
        for (let i = 0; i <= currentIndex; i++) {{
            const date = dates[i];
            const price = niftyPrices[date];
            if (price && niftyStartPrice) {{
                const val = 500000.0 * (price / niftyStartPrice);
                if (val > niftyPeak) {{
                    niftyPeak = val;
                }}
                const dd = ((niftyPeak - val) / niftyPeak) * 100.0;
                if (dd > niftyMaxDD) {{
                    niftyMaxDD = dd;
                }}
            }}
        }}

        // Render Nifty Benchmark Card
        niftyValDisplay.textContent = '₹' + niftyVal.toLocaleString('en-IN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
        niftyPnlDisplay.textContent = (niftyPnl >= 0 ? '+' : '') + '₹' + Math.abs(niftyPnl).toLocaleString('en-IN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
        niftyPnlDisplay.className = 'benchmark-val ' + (niftyPnl >= 0 ? 'positive' : 'negative');
        
        niftyPctDisplay.textContent = (niftyPct >= 0 ? '+' : '') + niftyPct.toFixed(2) + '%';
        niftyPctDisplay.className = 'benchmark-val ' + (niftyPct >= 0 ? 'positive' : 'negative');

        niftyCagrDisplay.textContent = niftyCagr === 'N/A' ? 'N/A' : niftyCagr;
        niftyCagrDisplay.className = 'benchmark-val ' + (niftyPct >= 0 ? 'positive' : 'negative');

        niftyMaxDdDisplay.textContent = '-' + niftyMaxDD.toFixed(2) + '%';

        // Populate Running, Exited, and Added Stocks Tables dynamically
        populateActivityTables(currentDate);

        // Prepare items for chart
        const items = etfs.map(etf => ({{
            etf: etf,
            val: dateData[etf] || 0.0
        }}));

        items.sort((a, b) => b.val - a.val);

        // Scaling limits (locked to global max absolute value)
        const maxVal = globalMaxAbs;

        // Redraw grid lines
        drawGrid(maxVal, labelWidth, valueWidth);

        // Dynamically adjust animation speed duration in ms matching playback speed
        const duration = isPlaying ? speed : 200;

        // Position, size and style each bar row
        items.forEach((item, index) => {{
            const row = document.getElementById(`row-${{item.etf}}`);
            const fill = document.getElementById(`fill-${{item.etf}}`);
            const valDiv = document.getElementById(`val-${{item.etf}}`);
            const labelDiv = document.getElementById(`lbl-${{item.etf}}`);

            // Apply dynamic transitions for smooth fluid flow (no jumping)
            row.style.transition = `top ${{duration}}ms cubic-bezier(0.25, 0.1, 0.25, 1), opacity ${{duration}}ms ease`;
            fill.style.transition = `width ${{duration}}ms cubic-bezier(0.25, 0.1, 0.25, 1)`;

            if (index < topN) {{
                // Apply dynamic layout overrides
                row.style.top = `${{index * rowOffset}}px`;
                row.style.height = `${{rowHeight}}px`;
                fill.style.height = `${{barHeight}}px`;
                labelDiv.style.width = labelWidth + 'px';
                labelDiv.style.fontSize = fontSize;
                valDiv.style.width = valueWidth + 'px';
                
                // Keep active items visible with correct opacity and pointer events
                row.style.pointerEvents = 'auto';

                // Highlighting active positions
                const isActive = activeList.includes(item.etf);
                if (isActive) {{
                    row.style.opacity = '1.0';
                    if (!labelDiv.querySelector('.active-indicator')) {{
                        labelDiv.innerHTML = `<span style="font-weight:600;">${{item.etf}}</span><span class="active-indicator"></span>`;
                    }}
                }} else {{
                    row.style.opacity = '0.35';
                    labelDiv.innerHTML = `<span style="font-weight:600;">${{item.etf}}</span>`;
                }}

                // Calculate percentage width (all bars start from left = 0)
                let pct = (Math.abs(item.val) / maxVal) * 100;
                if (pct < 1 && Math.abs(item.val) > 0) pct = 1;

                fill.style.width = `${{pct}}%`;

                // Handle green (profit) vs red (loss) visual gradients
                if (item.val >= 0) {{
                    fill.style.background = `linear-gradient(90deg, ${{colorMap[item.etf].greenBase}}, ${{colorMap[item.etf].greenLight}})`;
                    fill.style.boxShadow = isActive ? `0 0 10px ${{colorMap[item.etf].greenGlow}}` : 'none';
                    valDiv.className = 'bar-value positive';
                }} else {{
                    fill.style.background = `linear-gradient(90deg, ${{colorMap[item.etf].redBase}}, ${{colorMap[item.etf].redLight}})`;
                    fill.style.boxShadow = isActive ? `0 0 10px ${{colorMap[item.etf].redGlow}}` : 'none';
                    valDiv.className = 'bar-value negative';
                }}

                const valText = formatCurrency(item.val);
                valDiv.textContent = valText;

                // --- TEXT SHRINK LOGIC FOR VALUE DISPLAY ---
                // Scales down font size for long numbers (profits/losses) to prevent layout shifting
                const basePx = parseFloat(fontSize);
                let adjustedFontSize = fontSize;
                if (valText.length > 12) {{
                    adjustedFontSize = (basePx * 0.74) + 'px';
                }} else if (valText.length > 9) {{
                    adjustedFontSize = (basePx * 0.86) + 'px';
                }}
                valDiv.style.fontSize = adjustedFontSize;

            }} else {{
                // Animate rows exiting the top N gracefully down to the bottom and fade out
                row.style.top = `${{topN * rowOffset}}px`;
                row.style.opacity = '0';
                row.style.pointerEvents = 'none';
            }}
        }});
    }}

    function populateActivityTables(currentDate) {{
        runningBody.innerHTML = '';
        exitedBody.innerHTML = '';
        addedBody.innerHTML = '';

        const currentIdx = dates.indexOf(currentDate);

        const runningTrades = [];
        const exitedTrades = [];
        const addedTrades = [];

        tradesList.forEach(trade => {{
            const entryIdx = dates.indexOf(trade.entryDate);
            const exitIdx = dates.indexOf(trade.exitDate);

            // Determine if trade is active/running on currentDate
            let isRunning = false;
            if (trade.exitReason === 'EOP') {{
                isRunning = (entryIdx !== -1 && exitIdx !== -1 && entryIdx <= currentIdx && currentIdx <= exitIdx);
            }} else {{
                isRunning = (entryIdx !== -1 && exitIdx !== -1 && entryIdx <= currentIdx && currentIdx < exitIdx);
            }}

            // 1. Running stocks calculation (open positions on currentDate)
            if (isRunning) {{
                const currentPrice = prices[trade.stock] ? prices[trade.stock][currentDate] : null;
                const finalPrice = (currentPrice !== null && currentPrice !== undefined) ? currentPrice : trade.entryPrice;
                const pnl = (finalPrice - trade.entryPrice) * trade.qty;
                const pct = ((finalPrice / trade.entryPrice) - 1.0) * 100.0;

                runningTrades.push({{
                    stock: trade.stock,
                    entryPrice: trade.entryPrice,
                    qty: trade.qty,
                    currentPrice: finalPrice,
                    pnl: pnl,
                    pct: pct
                }});
            }}

            // 2. Exited stocks calculation (closed on currentDate, excluding EOP)
            if (trade.exitDate === currentDate && trade.exitReason !== 'EOP') {{
                const pct = ((trade.exitPrice / trade.entryPrice) - 1.0) * 100.0;
                exitedTrades.push({{
                    stock: trade.stock,
                    entryPrice: trade.entryPrice,
                    exitPrice: trade.exitPrice,
                    qty: trade.qty,
                    pnl: trade.pnl,
                    pct: pct
                }});
            }}

            // 3. Added stocks calculation (opened on currentDate)
            if (trade.entryDate === currentDate) {{
                addedTrades.push({{
                    stock: trade.stock,
                    entryPrice: trade.entryPrice,
                    qty: trade.qty,
                    amount: trade.entryPrice * trade.qty
                }});
            }}
        }});

        // Sort running positions by P&L magnitude (highest to lowest)
        runningTrades.sort((a, b) => b.pnl - a.pnl);

        // Render Running Stocks
        if (runningTrades.length === 0) {{
            runningBody.innerHTML = `<tr><td colspan="6" class="empty-row-msg">No active open positions on this date</td></tr>`;
        }} else {{
            runningTrades.forEach((t, i) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight:700; color: #60a5fa;">${{t.stock}}</td>
                    <td>₹${{t.entryPrice.toLocaleString('en-IN', {{minimumFractionDigits: 1}})}}</td>
                    <td>${{t.qty}}</td>
                    <td>₹${{t.currentPrice.toLocaleString('en-IN', {{minimumFractionDigits: 1}})}}</td>
                    <td class="${{t.pnl >= 0 ? 'text-green' : 'text-red'}}">${{t.pnl >= 0 ? '+' : ''}}₹${{Math.round(t.pnl).toLocaleString('en-IN')}}</td>
                    <td class="${{t.pct >= 0 ? 'text-green' : 'text-red'}}">${{t.pct >= 0 ? '+' : ''}}${{t.pct.toFixed(2)}}%</td>
                `;
                runningBody.appendChild(row);
            }});
        }}

        // Render Exited Stocks
        if (exitedTrades.length === 0) {{
            exitedBody.innerHTML = `<tr><td colspan="6" class="empty-row-msg">No closed positions on this date</td></tr>`;
        }} else {{
            exitedTrades.forEach((t, i) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight:700; color: #60a5fa;">${{t.stock}}</td>
                    <td>₹${{t.entryPrice.toLocaleString('en-IN', {{minimumFractionDigits: 1}})}}</td>
                    <td>₹${{t.exitPrice.toLocaleString('en-IN', {{minimumFractionDigits: 1}})}}</td>
                    <td>${{t.qty}}</td>
                    <td class="${{t.pnl >= 0 ? 'text-green' : 'text-red'}}">${{t.pnl >= 0 ? '+' : ''}}₹${{Math.round(t.pnl).toLocaleString('en-IN')}}</td>
                    <td class="${{t.pct >= 0 ? 'text-green' : 'text-red'}}">${{t.pct >= 0 ? '+' : ''}}${{t.pct.toFixed(2)}}%</td>
                `;
                exitedBody.appendChild(row);
            }});
        }}

        // Render Added Stocks
        if (addedTrades.length === 0) {{
            addedBody.innerHTML = `<tr><td colspan="4" class="empty-row-msg">No new positions opened on this date</td></tr>`;
        }} else {{
            addedTrades.forEach((t, i) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight:700; color: #60a5fa;">${{t.stock}}</td>
                    <td>₹${{t.entryPrice.toLocaleString('en-IN', {{minimumFractionDigits: 1}})}}</td>
                    <td>${{t.qty}}</td>
                    <td>₹${{Math.round(t.amount).toLocaleString('en-IN')}}</td>
                `;
                addedBody.appendChild(row);
            }});
        }}
    }}

    function drawGrid(maxVal, labelWidth, valueWidth) {{
        const gridContainer_ref = document.getElementById('grid-lines-container');
        gridContainer_ref.innerHTML = '';
        const steps = 4;
        
        const duration = isPlaying ? speed : 200;
        gridContainer_ref.style.transition = `left ${{duration}}ms ease, right ${{duration}}ms ease`;
        gridContainer_ref.style.left = `${{labelWidth}}px`;
        gridContainer_ref.style.right = `${{valueWidth}}px`;

        for (let i = 0; i <= steps; i++) {{
            const pct = (i / steps) * 100;
            const val = (i / steps) * maxVal;

            const gridLine = document.createElement('div');
            gridLine.className = 'grid-line';
            gridLine.style.left = `${{pct}}%`;

            const label = document.createElement('div');
            label.className = 'grid-label';
            label.textContent = formatCurrencyShort(val);

            gridLine.appendChild(label);
            gridContainer_ref.appendChild(gridLine);
        }}
    }}

    // Formatter helpers
    function formatCurrency(val) {{
        const sign = val >= 0 ? '+' : '-';
        return `${{sign}}₹${{Math.abs(val).toLocaleString('en-IN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;
    }}

    // Playback loop
    function togglePlay() {{
        if (isPlaying) {{
            pause();
        }} else {{
            play();
        }}
    }}

    function play() {{
        isPlaying = true;
        playText.textContent = 'Pause';
        playIcon.classList.add('hidden');
        pauseIcon.classList.remove('hidden');

        timer = setInterval(() => {{
            if (currentIndex < dates.length - 1) {{
                currentIndex++;
                updateFrame();
            }} else {{
                pause();
            }}
        }}, speed);
    }}

    function pause() {{
        isPlaying = false;
        playText.textContent = 'Play';
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
        clearInterval(timer);
    }}

    function resetChart() {{
        pause();
        currentIndex = 0;
        updateFrame();
    }}

    function updateSpeed(e) {{
        speed = 1100 - parseInt(e.target.value); 
        if (isPlaying) {{
            pause();
            play();
        }}
    }}

    function updateLimit(e) {{
        topN = parseInt(e.target.value);
        updateFrame();
    }}

    function scrubTimeline(e) {{
        pause();
        currentIndex = parseInt(e.target.value);
        updateFrame();
    }}

    // Run initialization
    window.onload = init;
</script>

</body>
</html>
"""

# 6. Write the compiled HTML to the workspace
output_path = "bar_chart_race.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCESS] Transposed and updated Bar Chart Race HTML successfully saved to {output_path}")
