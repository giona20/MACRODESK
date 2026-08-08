MACRODESK
Dual-desk macro + crypto monitor. All data sources free, no API keys.
Pages
app.py — war room: Duration Stress + Chokepoint indices, regime label, the 30Y fade rule
1 CPI Battle Plan — scenario grid, countdown, live distance to targets
2 Rates & Duration — curve, term premium, inflation expectations
3 Crypto & Hyperliquid — spot vs levels, live funding/OI, ETH/BTC
4 Geopolitics & Hormuz — AIS map, oil, filtered news, GDELT
5 Guide — plain-language explanation of every concept, gauge and rule (start here if new)
Core indicators
DURATION STRESS (0-100) — how hostile the long end is to risk assets.
30Y level 40% · 30Y momentum 25% · 2s30s steepening 20% · breakevens 15%.
CHOKEPOINT (0-100) — war/energy premium.
Oil momentum 40% · tankers 25% · defense 15% · GDELT news 20%.
THE FADE RULE — if BTC pops >0.8% and the 30Y hasn't fallen >2bp,
the move isn't confirmed by duration. Fade it.
Data sources
yfinance · FRED CSV · CoinGecko · Hyperliquid info API · Polymarket Gamma ·
Google News RSS · GDELT 2.0 · VesselFinder/MarineTraffic embeds
Deploy
Push to GitHub → Streamlit Cloud → main file `app.py`.
Edit `LEVELS`, `CPI_GRID` and `EVENTS` in `core.py` to update the playbook.
