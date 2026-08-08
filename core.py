"""
MACRODESK — shared data layer.
All sources free / keyless: yfinance, FRED CSV, Google News RSS, GDELT,
Polymarket Gamma, CoinGecko public, Hyperliquid public API, Farside (scrape).
Every fetcher fails soft: returns empty, never raises into the UI.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import re
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

UA = {"User-Agent": "Mozilla/5.0 (MacroDesk dashboard; personal use)"}

# ---------------------------------------------------------------- symbols
TK = {
    # rates (the spine)
    "US30Y": "^TYX",      # 30-year yield  (TVC:US30Y equivalent)
    "US10Y": "^TNX",      # 10-year yield
    "US02Y": "^FVX",      # 5y proxy; 2y via FRED below (yf has no clean ^IRX 2y)
    # macro
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "GOLD": "GC=F",
    "BRENT": "BZ=F",
    "WTI": "CL=F",
    "SPX": "^GSPC",
    "NDX": "^NDX",
    # crypto
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}
TANKERS = ["FRO", "STNG", "TNK", "INSW"]
DEFENSE = ["LMT", "RTX", "NOC", "GD"]

# FRED series (CSV endpoint is public, no key)
FRED = {
    "DGS30": "30Y Treasury",
    "DGS10": "10Y Treasury",
    "DGS2": "2Y Treasury",
    "T10YIE": "10Y breakeven inflation",
    "T5YIFR": "5y5y forward inflation",
    "THREEFYTP10": "10Y term premium (ACM)",
}

# ---- key levels from the playbook (edit here, propagates everywhere)
LEVELS = {
    "BTC": {"support": [63800, 61800, 56000], "resistance": [65135, 67300, 70000],
            "note": "63.8K break point · 65.1K 50d EMA · 67.3K regime change"},
    "ETH": {"support": [1870, 1820, 1700], "resistance": [2000, 2150, 2250],
            "note": "2000 is the line"},
    "HYPE": {"support": [52.48, 51.14, 47.0], "resistance": [56.17, 60.43, 63.45],
             "note": "56.17 wedge · 52.48 DANGER (liquidation cascade)"},
}

CPI_GRID = [
    {"print": "≤0.1%", "odds": 15, "tag": "🟢 miracle",
     "BTC": "67.3K → 70K", "ETH": "2000 → 2200", "HYPE": "60.4 → 63.4",
     "desc": "Only print that pulls 30Y down. Term premium compresses."},
    {"print": "0.2%", "odds": 35, "tag": "🟡 in line",
     "BTC": "65–66K chop", "ETH": "1950–2000", "HYPE": "56–58",
     "desc": "Modest relief. If 30Y stays 5.22 → fade the pop."},
    {"print": "0.3%", "odds": 35, "tag": "🟠 as forecast",
     "BTC": "61.8–63.1K", "ETH": "1820–1870", "HYPE": "51.1 → 50.0",
     "desc": "Re-acceleration from June 0.00%. Validates the 3 dissenters."},
    {"print": "≥0.4%", "odds": 15, "tag": "🔴 passthrough",
     "BTC": "56–58K", "ETH": "1700–1750", "HYPE": "47 → 43",
     "desc": "Long-duration assets hit hardest. Sept hike near-certain."},
]

EVENTS = [
    ("2026-08-11 12:00", "NFIB small business", "🟡", "Prices/hiring sub-indices"),
    ("2026-08-11 18:00", "Cleveland Fed nowcast (final)", "🟠",
     "Best single pre-CPI estimate"),
    ("2026-08-12 14:30", "JULY CPI", "🔴", "THE PRINT — core m/m is the number"),
    ("2026-08-13 14:30", "July PPI", "🟠", "Input costs — confirms/denies CPI"),
    ("2026-08-14 14:30", "Retail Sales", "🟡", "Gas crowding out discretionary?"),
    ("2026-08-14 16:00", "UMich prelim", "🟡", "Inflation expectations"),
    ("2026-08-17 16:00", "NAHB housing", "🟡", "Rate sensitivity"),
    ("2026-08-18 14:30", "Housing starts", "🟡", "Permits lead starts"),
    ("2026-08-19 16:30", "EIA crude inventories", "🟠", "Physical tightness"),
    ("2026-08-19 20:00", "FOMC minutes (Jul 29)", "🟠", "How hard was the hike debate?"),
    ("2026-08-21 00:00", "JACKSON HOLE begins", "🔴",
     "Theme: Financial Innovation / CBDCs. Warsh course-correction?"),
    ("2026-09-11 00:00", "Senate returns", "🟠", "CLARITY window reopens"),
    ("2026-09-16 20:00", "FOMC + dot plot", "🔴", "Where a hike lands if it comes"),
]


# ---------------------------------------------------------------- fetchers
@st.cache_data(ttl=300, show_spinner=False)
def market(days: int = 180) -> pd.DataFrame:
    syms = list(TK.values()) + TANKERS + DEFENSE
    try:
        end = dt.datetime.utcnow()
        df = yf.download(syms, start=end - dt.timedelta(days=days), end=end,
                         progress=False, auto_adjust=True)["Close"]
        if isinstance(df, pd.Series):
            df = df.to_frame()
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def fred(series: str, obs: int = 400) -> pd.DataFrame:
    """FRED public CSV — no API key."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    try:
        r = requests.get(url, headers=UA, timeout=15)
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna().tail(obs).reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["date", "value"])


@st.cache_data(ttl=300, show_spinner=False)
def crypto_spot() -> dict:
    """CoinGecko public endpoint — BTC/ETH/HYPE spot + 24h."""
    out = {}
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,hyperliquid",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true"},
            headers=UA, timeout=12)
        js = r.json()
        m = {"bitcoin": "BTC", "ethereum": "ETH", "hyperliquid": "HYPE"}
        for k, v in m.items():
            if k in js:
                out[v] = {"price": js[k].get("usd"),
                          "chg": js[k].get("usd_24h_change"),
                          "vol": js[k].get("usd_24h_vol")}
    except Exception:
        pass
    return out


@st.cache_data(ttl=300, show_spinner=False)
def hyperliquid_meta() -> pd.DataFrame:
    """Hyperliquid public info API — funding, OI, mark px for perps."""
    try:
        r = requests.post("https://api.hyperliquid.xyz/info",
                          json={"type": "metaAndAssetCtxs"},
                          headers={**UA, "Content-Type": "application/json"},
                          timeout=12)
        meta, ctxs = r.json()
        rows = []
        for u, c in zip(meta["universe"], ctxs):
            rows.append({
                "coin": u["name"],
                "mark": float(c.get("markPx") or 0),
                "funding": float(c.get("funding") or 0) * 100,   # % per hour
                "oi": float(c.get("openInterest") or 0),
                "vol24h": float(c.get("dayNtlVlm") or 0),
            })
        df = pd.DataFrame(rows)
        df["oi_usd"] = df["oi"] * df["mark"]
        return df.sort_values("vol24h", ascending=False)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def polymarket(terms: tuple[str, ...]) -> list[dict]:
    out = []
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets",
                         params={"active": "true", "closed": "false",
                                 "limit": 400, "order": "volume24hr",
                                 "ascending": "false"},
                         headers=UA, timeout=15)
        for m in r.json():
            q = (m.get("question") or "").lower()
            if any(t in q for t in terms):
                try:
                    p = m.get("outcomePrices")
                    if isinstance(p, str):
                        p = json.loads(p)
                    yes = float(p[0]) * 100 if p else None
                except Exception:
                    yes = None
                out.append({"q": m.get("question"), "yes": yes,
                            "vol": float(m.get("volume24hr") or 0),
                            "url": "https://polymarket.com/event/" +
                                   (m.get("slug") or "")})
    except Exception:
        pass
    return sorted(out, key=lambda x: -x["vol"])[:12]


@st.cache_data(ttl=900, show_spinner=False)
def news(keyword: str, n: int = 6) -> list[dict]:
    try:
        import feedparser
        url = (f"https://news.google.com/rss/search?q={quote_plus(keyword)}"
               "&hl=en-US&gl=US&ceid=US:en")
        f = feedparser.parse(url)
        return [{"title": e.get("title", ""), "link": e.get("link", ""),
                 "pub": e.get("published", ""), "kw": keyword}
                for e in f.entries[:n]]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def gdelt(query: str, days: int = 45) -> pd.DataFrame:
    url = ("https://api.gdeltproject.org/api/v2/doc/doc"
           f"?query={quote_plus(query)}&mode=timelinevol"
           f"&timespan={days}d&format=json")
    try:
        js = requests.get(url, headers=UA, timeout=15).json()
        df = pd.DataFrame(js["timeline"][0]["data"])
        df["date"] = pd.to_datetime(df["date"])
        return df.rename(columns={"value": "vol"})[["date", "vol"]]
    except Exception:
        return pd.DataFrame(columns=["date", "vol"])


# ---------------------------------------------------------------- helpers
def chg(s: pd.Series, d: int) -> float:
    s = s.dropna()
    return np.nan if len(s) <= d else (s.iloc[-1] / s.iloc[-1 - d] - 1) * 100


def bps(s: pd.Series, d: int) -> float:
    """Yield change in basis points (yf yields are in %*10 for ^TYX/^TNX)."""
    s = s.dropna()
    return np.nan if len(s) <= d else (s.iloc[-1] - s.iloc[-1 - d]) * 10


def scale(x, lo, hi):
    return np.nan if (x is None or np.isnan(x)) else float(np.clip((x - lo) / (hi - lo), 0, 1))


def basket(h: pd.DataFrame, t: list[str]) -> pd.Series:
    c = [x for x in t if x in h.columns]
    return h[c].mean(axis=1) if c else pd.Series(dtype=float)


# ---------------------------------------------------------------- indicators
def duration_stress(h: pd.DataFrame, tp: pd.DataFrame) -> dict:
    """DURATION STRESS INDEX (0-100) — the core proprietary indicator.

    Answers: how hostile is the long end to risk assets right now?
    High = crypto's discount rate is bad regardless of Fed meeting odds.
      40% 30Y level (4.0-5.5% band)
      25% 30Y 10d momentum (is it still selling off?)
      20% 2s30s steepening (bear steepener = credibility problem)
      15% 10y breakeven (market inflation expectation)
    """
    comp, notes = {}, {}
    y30 = h.get(TK["US30Y"], pd.Series(dtype=float)).dropna() / 10  # ^TYX -> %
    y10 = h.get(TK["US10Y"], pd.Series(dtype=float)).dropna() / 10

    lvl = y30.iloc[-1] if len(y30) else np.nan
    comp["30Y level"] = scale(lvl, 4.0, 5.5)
    notes["30Y level"] = f"{lvl:.2f}%" if not np.isnan(lvl) else "n/a"

    mom = (y30.iloc[-1] - y30.iloc[-11]) * 100 if len(y30) > 11 else np.nan
    comp["30Y momentum"] = scale(mom, -20, 30)
    notes["30Y momentum"] = f"{mom:+.0f}bp / 10d" if not np.isnan(mom) else "n/a"

    # 2s30s via FRED (yf lacks a clean 2y)
    d2 = fred("DGS2"); d30 = fred("DGS30")
    steep = np.nan
    if not d2.empty and not d30.empty:
        cur = d30["value"].iloc[-1] - d2["value"].iloc[-1]
        prv = (d30["value"].iloc[-11] - d2["value"].iloc[-11]
               if len(d2) > 11 and len(d30) > 11 else np.nan)
        steep = (cur - prv) * 100 if not np.isnan(prv) else np.nan
        notes["2s30s steepening"] = (f"curve {cur:.2f}% ({steep:+.0f}bp/10d)"
                                     if not np.isnan(steep) else f"curve {cur:.2f}%")
    else:
        notes["2s30s steepening"] = "n/a"
    comp["2s30s steepening"] = scale(steep, -20, 40)

    be = np.nan
    if not tp.empty:
        be = tp["value"].iloc[-1]
    comp["Inflation expectations"] = scale(be, 2.0, 3.2)
    notes["Inflation expectations"] = f"10y breakeven {be:.2f}%" if not np.isnan(be) else "n/a"

    w = {"30Y level": .40, "30Y momentum": .25,
         "2s30s steepening": .20, "Inflation expectations": .15}
    tot = ws = 0.0
    for k, wt in w.items():
        if not np.isnan(comp.get(k, np.nan)):
            tot += comp[k] * wt; ws += wt
    return {"index": round(tot / ws * 100) if ws else None,
            "components": comp, "notes": notes, "weights": w}


def hormuz_risk(h: pd.DataFrame, g: pd.DataFrame) -> dict:
    """CHOKEPOINT sub-index (0-100) — war/energy premium."""
    comp, notes = {}, {}
    b = h.get(TK["BRENT"], pd.Series(dtype=float))
    w_ = h.get(TK["WTI"], pd.Series(dtype=float))
    bm = chg(b, 5)
    sp = (b.dropna().iloc[-1] - w_.dropna().iloc[-1]
          if len(b.dropna()) and len(w_.dropna()) else np.nan)
    comp["Oil momentum"] = scale(bm, -5, 10)
    notes["Oil momentum"] = f"Brent 5d {bm:+.1f}% · spread ${sp:.2f}" if not np.isnan(bm) else "n/a"

    tk = chg(basket(h, TANKERS), 5)
    comp["Tanker premium"] = scale(tk, -5, 12)
    notes["Tanker premium"] = f"{tk:+.1f}% 5d" if not np.isnan(tk) else "n/a"

    df_ = chg(basket(h, DEFENSE), 10)
    comp["Defense bid"] = scale(df_, -5, 8)
    notes["Defense bid"] = f"{df_:+.1f}% 10d" if not np.isnan(df_) else "n/a"

    if not g.empty:
        v = g["vol"]
        comp["News intensity"] = scale(v.iloc[-1], v.min(), v.max())
        notes["News intensity"] = f"{v.iloc[-1]:.2f} (range {v.min():.2f}–{v.max():.2f})"
    else:
        comp["News intensity"] = np.nan; notes["News intensity"] = "n/a"

    w = {"Oil momentum": .40, "Tanker premium": .25,
         "Defense bid": .15, "News intensity": .20}
    tot = ws = 0.0
    for k, wt in w.items():
        if not np.isnan(comp.get(k, np.nan)):
            tot += comp[k] * wt; ws += wt
    return {"index": round(tot / ws * 100) if ws else None,
            "components": comp, "notes": notes, "weights": w}


def regime(dur: int | None, horm: int | None, btc_chg: float | None) -> tuple[str, str, str]:
    """Melt the engines into one regime label."""
    if dur is None:
        return "NO DATA", "gray", "Feeds unavailable."
    if dur >= 70 and (horm or 0) >= 55:
        return ("FULL BEAR", "#c62828",
                "Duration hostile + war premium. Long-duration assets punished. "
                "Short bias, wide MM, no grid.")
    if dur >= 70:
        return ("DURATION SQUEEZE", "#ef6c00",
                "Long end hostile regardless of Fed odds. Fade crypto pops — "
                "the 4/4 rule is live.")
    if dur >= 45:
        return ("TENSE / RANGE", "#f9a825",
                "Nothing resolved. Chop favours MM, punishes directional size.")
    if dur < 45 and (horm or 0) < 40:
        return ("RELIEF", "#2e7d32",
                "Term premium compressing + war premium deflating. "
                "This is the regime where crypto rallies stick.")
    return ("MIXED", "#f9a825", "Engines disagree — reduce size, wait for alignment.")


def fade_rule(h: pd.DataFrame) -> tuple[bool, str]:
    """THE ONE RULE: did the 30Y rally today? If not, fade crypto pops."""
    y30 = h.get(TK["US30Y"], pd.Series(dtype=float)).dropna() / 10
    btc = h.get(TK["BTC"], pd.Series(dtype=float)).dropna()
    if len(y30) < 2 or len(btc) < 2:
        return False, "insufficient data"
    dy = (y30.iloc[-1] - y30.iloc[-2]) * 100
    db = (btc.iloc[-1] / btc.iloc[-2] - 1) * 100
    if db > 0.8 and dy > -2:
        return True, (f"BTC {db:+.1f}% but 30Y {dy:+.0f}bp — "
                      "pop NOT confirmed by the long end. FADE.")
    if db > 0.8 and dy <= -2:
        return False, (f"BTC {db:+.1f}% and 30Y {dy:+.0f}bp — "
                       "confirmed by duration. Real move.")
    return False, f"BTC {db:+.1f}% · 30Y {dy:+.0f}bp — no signal."


def level_proximity(price: float, sym: str) -> list[dict]:
    """Distance to each key level, sorted by nearness."""
    if not price or sym not in LEVELS:
        return []
    out = []
    for kind in ("support", "resistance"):
        for lv in LEVELS[sym][kind]:
            out.append({"level": lv, "kind": kind,
                        "dist_pct": (lv / price - 1) * 100})
    return sorted(out, key=lambda x: abs(x["dist_pct"]))
