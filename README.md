MACRODESK
Dual-desk macro + crypto monitor. All data sources free, no API keys.
Pages
app.py — war room: Duration Stress + Chokepoint indices, regime label, the 30Y fade rule
1 CPI Battle Plan — scenario grid, countdown, live distance to targets
2 Rates & Duration — curve, term premium, inflation expectations
3 Crypto & Hyperliquid — spot vs levels, live funding/OI, ETH/BTC
4 Geopolitics & Hormuz — AIS map, oil, filtered news, GDELT
5 Guide — 10-tab plain-language manual: concepts, data releases, the Fed, war/oil, crypto mechanics, chart reading, routine, dictionary
6 Terminal — Bloomberg-style candlestick grid, ASCII tape, multi-timeframe, correlation matrix
7 Diagnostics — live feed health. If anything looks blank or wrong, start here.
Core indicators
DURATION STRESS (0-100) — how hostile the long end is to risk assets.
30Y level 40% · 30Y momentum 25% · 2s30s steepening 20% · breakevens 15%.
CHOKEPOINT (0-100) — war/energy premium.
Oil momentum 40% · tankers 25% · defense 15% · GDELT news 20%.
THE FADE RULE — if BTC pops >0.8% and the 30Y hasn't fallen >2bp,
the move isn't confirmed by duration. Fade it.
Data sources (multi-source with fallbacks — no single provider can blank the app)
Data	Primary	Fallback
Yields	FRED CSV	Stooq → yfinance
Equities/commodities	yfinance	Stooq CSV
Crypto spot	CoinGecko	Binance
Perps	Hyperliquid info API	—
News	Google RSS · GDELT	—
Markets	Polymarket Gamma	—
All keyless. Every fetch logs status to the Diagnostics page.
Troubleshooting
Blank page → open 🔧 Diagnostics → Clear cache and re-fetch.
Most common cause is Yahoo rate-limiting the Streamlit Cloud shared IP;
the Stooq fallback covers most of it, and redeploying gets a fresh IP.
Deploy
Push to GitHub → Streamlit Cloud → main file `app.py`.
Edit `LEVELS`, `CPI_GRID` and `EVENTS` in `core.py` to update the playbook.
