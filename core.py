"""
MACRODESK — shared data layer (resilient multi-source).

Design rule: NO SILENT FAILURES. Every fetch records status in FEED_LOG so the
Diagnostics page can show exactly what's alive. Every source has a fallback:

  yields  : FRED CSV  -> Stooq CSV  -> yfinance
  crypto  : CoinGecko -> Binance    -> yfinance
  equities: yfinance  -> Stooq CSV
  news    : Google RSS ; GDELT ; Polymarket Gamma  (all keyless)
"""
from __future__ import annotations

import datetime as dt
import io
import json
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import requests
import streamlit as st

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0 Safari/537.36"}

# feed status -> {name: (ok: bool, detail: str)}
if "FEED_LOG" not in st.session_state:
    st.session_state.FEED_LOG = {}


def _log(name: str, ok: bool, detail: str = "") -> None:
    try:
        st.session_state.FEED_LOG[name] = (ok, detail)
    except Exception:
        pass


# ---------------------------------------------------------------- symbols
TK = {
    "US30Y": "^TYX", "US10Y": "^TNX", "US05Y": "^FVX",
    "DXY": "DX-Y.NYB", "VIX": "^VIX", "GOLD": "GC=F",
    "BRENT": "BZ=F", "WTI": "CL=F", "SPX": "^GSPC", "NDX": "^NDX",
    "BTC": "BTC-USD", "ETH": "ETH-USD",
}
# Stooq fallback symbols (free CSV, no key, no rate limit)
STOOQ = {
    "^TYX": "30usy.b", "^TNX": "10usy.b", "^FVX": "5usy.b",
    "^GSPC": "^spx", "^NDX": "^ndx", "^VIX": "^vix",
    "GC=F": "xauusd", "BZ=F": "cb.f", "CL=F": "cl.f",
    "BTC-USD": "btcusd", "ETH-USD": "ethusd", "DX-Y.NYB": "dx.f",
}
TANKERS = ["FRO", "STNG", "TNK", "INSW"]
DEFENSE = ["LMT", "RTX", "NOC", "GD"]

FRED = {
    "DGS30": "30Y Treasury", "DGS10": "10Y Treasury", "DGS2": "2Y Treasury",
    "T10YIE": "10Y breakeven inflation", "T5YIFR": "5y5y forward inflation",
    "THREEFYTP10": "10Y term premium (ACM)",
}
# FRED id for each yfinance yield ticker (preferred source)
FRED_FOR = {"^TYX": "DGS30", "^TNX": "DGS10", "^FVX": "DGS5"}

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
    ("2026-08-11 18:00", "Cleveland Fed nowcast (final)", "🟠", "Best pre-CPI estimate"),
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


# ---------------------------------------------------------------- primitives
@st.cache_data(ttl=1800, show_spinner=False)
def stooq(symbol: str) -> pd.DataFrame:
    """Stooq free CSV — no key, no rate limit. Returns OHLC df indexed by date."""
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    try:
        r = requests.get(url, headers=UA, timeout=15)
        if r.status_code != 200 or "Date" not in r.text[:200]:
            _log(f"stooq:{symbol}", False, f"HTTP {r.status_code}")
            return pd.DataFrame()
        df = pd.read_csv(io.StringIO(r.text))
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date").sort_index()
        _log(f"stooq:{symbol}", True, f"{len(df)} rows")
        return df
    except Exception as e:
        _log(f"stooq:{symbol}", False, type(e).__name__)
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def fred(series: str, obs: int = 500) -> pd.DataFrame:
    for host in ("https://fred.stlouisfed.org/graph/fredgraph.csv?id=",
                 "https://www.stlouisfed.org/-/media/fred/graph/fredgraph.csv?id="):
        try:
            r = requests.get(host + series, headers=UA, timeout=15)
            if r.status_code != 200 or "," not in r.text[:200]:
                continue
            df = pd.read_csv(io.StringIO(r.text))
            df.columns = ["date", "value"]
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df.dropna().tail(obs).reset_index(drop=True)
            _log(f"fred:{series}", True, f"{len(df)} rows")
            return df
        except Exception as e:
            _log(f"fred:{series}", False, type(e).__name__)
    _log(f"fred:{series}", False, "all hosts failed")
    return pd.DataFrame(columns=["date", "value"])


@st.cache_data(ttl=600, show_spinner=False)
def yahoo(symbols: list[str], days: int) -> pd.DataFrame:
    try:
        import yfinance as yf
        end = dt.datetime.utcnow()
        df = yf.download(symbols, start=end - dt.timedelta(days=days), end=end,
                         progress=False, auto_adjust=True, threads=False)
        if df is None or df.empty:
            _log("yfinance", False, "empty response (Yahoo may be blocking)")
            return pd.DataFrame()
        close = df["Close"] if "Close" in df else df
        if isinstance(close, pd.Series):
            close = close.to_frame()
        close = close.dropna(how="all")
        _log("yfinance", not close.empty,
             f"{close.shape[1]} symbols, {len(close)} rows")
        return close
    except Exception as e:
        _log("yfinance", False, f"{type(e).__name__}: {e}"[:90])
        return pd.DataFrame()


def _norm_yield(s: pd.Series) -> pd.Series:
    """yfinance yield tickers sometimes quote %*10. Auto-detect and normalise."""
    s = s.dropna()
    if len(s) and s.iloc[-1] > 20:
        return s / 10
    return s


# ---------------------------------------------------------------- market
@st.cache_data(ttl=600, show_spinner=False)
def market(days: int = 240) -> pd.DataFrame:
    """Close prices for everything. Yahoo first, Stooq fills any gaps.
    Yields are ALWAYS normalised to percent (5.22 = 5.22%)."""
    want = list(TK.values()) + TANKERS + DEFENSE
    out = yahoo(want, days)

    missing = [s for s in want if s not in out.columns
               or out[s].dropna().empty]
    filled = []
    for sym in missing:
        alt = STOOQ.get(sym)
        if not alt:
            continue
        d = stooq(alt)
        if not d.empty and "Close" in d:
            out = out.join(d["Close"].rename(sym), how="outer") \
                if not out.empty else d[["Close"]].rename(columns={"Close": sym})
            filled.append(sym)

    # yields: prefer FRED (cleanest), else normalise whatever we have
    for tkr, fid in FRED_FOR.items():
        f = fred(fid)
        if not f.empty:
            s = f.set_index("date")["value"]
            out = out.drop(columns=[tkr], errors="ignore")
            out = out.join(s.rename(tkr), how="outer") if not out.empty \
                else s.rename(tkr).to_frame()
        elif tkr in out.columns:
            out[tkr] = _norm_yield(out[tkr])

    if filled:
        _log("stooq-fallback", True, f"filled {len(filled)}: {','.join(filled[:6])}")
    if out.empty:
        _log("market", False, "ALL SOURCES FAILED")
    else:
        out = out.sort_index()
        _log("market", True, f"{out.shape[1]} cols, {len(out)} rows")
    return out


@st.cache_data(ttl=300, show_spinner=False)
def crypto_spot() -> dict:
    """CoinGecko -> Binance fallback."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                         params={"ids": "bitcoin,ethereum,hyperliquid",
                                 "vs_currencies": "usd",
                                 "include_24hr_change": "true"},
                         headers=UA, timeout=12)
        if r.status_code == 200:
            js = r.json()
            m = {"bitcoin": "BTC", "ethereum": "ETH", "hyperliquid": "HYPE"}
            out = {v: {"price": js[k].get("usd"), "chg": js[k].get("usd_24h_change")}
                   for k, v in m.items() if k in js}
            if out:
                _log("coingecko", True, f"{len(out)} coins")
                return out
        _log("coingecko", False, f"HTTP {r.status_code}")
    except Exception as e:
        _log("coingecko", False, type(e).__name__)

    out = {}
    for sym, pair in (("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("HYPE", "HYPEUSDT")):
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/24hr",
                             params={"symbol": pair}, headers=UA, timeout=10)
            if r.status_code == 200:
                j = r.json()
                out[sym] = {"price": float(j["lastPrice"]),
                            "chg": float(j["priceChangePercent"])}
        except Exception:
            pass
    _log("binance", bool(out), f"{len(out)} coins")
    return out


@st.cache_data(ttl=300, show_spinner=False)
def hyperliquid_meta() -> pd.DataFrame:
    try:
        r = requests.post("https://api.hyperliquid.xyz/info",
                          json={"type": "metaAndAssetCtxs"},
                          headers={**UA, "Content-Type": "application/json"},
                          timeout=12)
        meta, ctxs = r.json()
        rows = [{"coin": u["name"], "mark": float(c.get("markPx") or 0),
                 "funding": float(c.get("funding") or 0) * 100,
                 "oi": float(c.get("openInterest") or 0),
                 "vol24h": float(c.get("dayNtlVlm") or 0)}
                for u, c in zip(meta["universe"], ctxs)]
        df = pd.DataFrame(rows)
        df["oi_usd"] = df["oi"] * df["mark"]
        _log("hyperliquid", True, f"{len(df)} perps")
        return df.sort_values("vol24h", ascending=False)
    except Exception as e:
        _log("hyperliquid", False, type(e).__name__)
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
                            "url": "https://polymarket.com/event/" + (m.get("slug") or "")})
        _log("polymarket", True, f"{len(out)} matched")
    except Exception as e:
        _log("polymarket", False, type(e).__name__)
    return sorted(out, key=lambda x: -x["vol"])[:12]


@st.cache_data(ttl=900, show_spinner=False)
def news(keyword: str, n: int = 6) -> list[dict]:
    try:
        import feedparser
        f = feedparser.parse(
            f"https://news.google.com/rss/search?q={quote_plus(keyword)}"
            "&hl=en-US&gl=US&ceid=US:en")
        res = [{"title": e.get("title", ""), "link": e.get("link", ""),
                "pub": e.get("published", ""), "kw": keyword} for e in f.entries[:n]]
        _log("googlenews", bool(res), f"{len(res)} items")
        return res
    except Exception as e:
        _log("googlenews", False, type(e).__name__)
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def gdelt(query: str, days: int = 45) -> pd.DataFrame:
    try:
        js = requests.get("https://api.gdeltproject.org/api/v2/doc/doc"
                          f"?query={quote_plus(query)}&mode=timelinevol"
                          f"&timespan={days}d&format=json",
                          headers=UA, timeout=15).json()
        df = pd.DataFrame(js["timeline"][0]["data"])
        df["date"] = pd.to_datetime(df["date"])
        _log("gdelt", True, f"{len(df)} points")
        return df.rename(columns={"value": "vol"})[["date", "vol"]]
    except Exception as e:
        _log("gdelt", False, type(e).__name__)
        return pd.DataFrame(columns=["date", "vol"])


# ---------------------------------------------------------------- helpers
def series(h: pd.DataFrame, key: str) -> pd.Series:
    """Safe accessor by friendly name ('US30Y','BTC'). Always percent for yields."""
    col = TK.get(key, key)
    if h is None or h.empty or col not in h.columns:
        return pd.Series(dtype=float)
    return h[col].dropna()


def chg(s: pd.Series, d: int) -> float:
    s = s.dropna()
    return np.nan if len(s) <= d else (s.iloc[-1] / s.iloc[-1 - d] - 1) * 100


def scale(x, lo, hi):
    try:
        if x is None or np.isnan(x):
            return np.nan
    except TypeError:
        return np.nan
    return float(np.clip((x - lo) / (hi - lo), 0, 1))


def basket(h: pd.DataFrame, t: list[str]) -> pd.Series:
    c = [x for x in t if h is not None and not h.empty and x in h.columns]
    return h[c].mean(axis=1) if c else pd.Series(dtype=float)


def data_ok(h: pd.DataFrame) -> bool:
    return h is not None and not h.empty and h.shape[1] >= 3


# ---------------------------------------------------------------- indicators
def duration_stress(h: pd.DataFrame, tp: pd.DataFrame) -> dict:
    comp, notes = {}, {}
    y30 = series(h, "US30Y")

    lvl = y30.iloc[-1] if len(y30) else np.nan
    comp["30Y level"] = scale(lvl, 4.0, 5.5)
    notes["30Y level"] = f"{lvl:.2f}%" if len(y30) else "no data"

    mom = (y30.iloc[-1] - y30.iloc[-11]) * 100 if len(y30) > 11 else np.nan
    comp["30Y momentum"] = scale(mom, -20, 30)
    notes["30Y momentum"] = f"{mom:+.0f}bp / 10d" if not np.isnan(mom) else "no data"

    d2, d30 = fred("DGS2"), fred("DGS30")
    steep = np.nan
    if not d2.empty and not d30.empty and len(d2) > 11 and len(d30) > 11:
        cur = d30["value"].iloc[-1] - d2["value"].iloc[-1]
        prv = d30["value"].iloc[-11] - d2["value"].iloc[-11]
        steep = (cur - prv) * 100
        notes["2s30s steepening"] = f"curve {cur:.2f}% ({steep:+.0f}bp/10d)"
    else:
        notes["2s30s steepening"] = "no data"
    comp["2s30s steepening"] = scale(steep, -20, 40)

    be = tp["value"].iloc[-1] if (tp is not None and not tp.empty) else np.nan
    comp["Inflation expectations"] = scale(be, 2.0, 3.2)
    notes["Inflation expectations"] = (f"10y breakeven {be:.2f}%"
                                       if not np.isnan(be) else "no data")

    w = {"30Y level": .40, "30Y momentum": .25,
         "2s30s steepening": .20, "Inflation expectations": .15}
    tot = ws = 0.0
    for k, wt in w.items():
        v = comp.get(k, np.nan)
        if not (v is None or np.isnan(v)):
            tot += v * wt; ws += wt
    return {"index": round(tot / ws * 100) if ws else None,
            "components": comp, "notes": notes, "weights": w,
            "coverage": round(ws * 100)}


def hormuz_risk(h: pd.DataFrame, g: pd.DataFrame) -> dict:
    comp, notes = {}, {}
    b, w_ = series(h, "BRENT"), series(h, "WTI")
    bm = chg(b, 5)
    sp = (b.iloc[-1] - w_.iloc[-1]) if (len(b) and len(w_)) else np.nan
    comp["Oil momentum"] = scale(bm, -5, 10)
    notes["Oil momentum"] = (f"Brent 5d {bm:+.1f}% · spread ${sp:.2f}"
                             if not np.isnan(bm) else "no data")

    tk = chg(basket(h, TANKERS), 5)
    comp["Tanker premium"] = scale(tk, -5, 12)
    notes["Tanker premium"] = f"{tk:+.1f}% 5d" if not np.isnan(tk) else "no data"

    df_ = chg(basket(h, DEFENSE), 10)
    comp["Defense bid"] = scale(df_, -5, 8)
    notes["Defense bid"] = f"{df_:+.1f}% 10d" if not np.isnan(df_) else "no data"

    if g is not None and not g.empty:
        v = g["vol"]
        comp["News intensity"] = scale(v.iloc[-1], v.min(), v.max())
        notes["News intensity"] = f"{v.iloc[-1]:.2f} (range {v.min():.2f}–{v.max():.2f})"
    else:
        comp["News intensity"] = np.nan; notes["News intensity"] = "no data"

    w = {"Oil momentum": .40, "Tanker premium": .25,
         "Defense bid": .15, "News intensity": .20}
    tot = ws = 0.0
    for k, wt in w.items():
        v = comp.get(k, np.nan)
        if not (v is None or np.isnan(v)):
            tot += v * wt; ws += wt
    return {"index": round(tot / ws * 100) if ws else None,
            "components": comp, "notes": notes, "weights": w,
            "coverage": round(ws * 100)}


def regime(dur, horm, btc_chg=None):
    if dur is None:
        return "NO DATA", "gray", "Feeds unavailable — see Diagnostics page."
    if dur >= 70 and (horm or 0) >= 55:
        return ("FULL BEAR", "#c62828",
                "Duration hostile + war premium. Short bias, wide MM, no grid.")
    if dur >= 70:
        return ("DURATION SQUEEZE", "#ef6c00",
                "Long end hostile regardless of Fed odds. Fade crypto pops.")
    if dur >= 45:
        return ("TENSE / RANGE", "#f9a825",
                "Nothing resolved. Chop favours MM, punishes directional size.")
    if (horm or 0) < 40:
        return ("RELIEF", "#2e7d32",
                "Term premium compressing + war premium deflating. Rallies stick.")
    return ("MIXED", "#f9a825", "Engines disagree — reduce size, wait for alignment.")


def fade_rule(h: pd.DataFrame) -> tuple[bool, str]:
    y30, btc = series(h, "US30Y"), series(h, "BTC")
    if len(y30) < 2 or len(btc) < 2:
        return False, "insufficient data — check Diagnostics"
    dy = (y30.iloc[-1] - y30.iloc[-2]) * 100
    db = (btc.iloc[-1] / btc.iloc[-2] - 1) * 100
    if db > 0.8 and dy > -2:
        return True, (f"BTC {db:+.1f}% but 30Y {dy:+.0f}bp — "
                      "pop NOT confirmed by the long end. FADE.")
    if db > 0.8:
        return False, (f"BTC {db:+.1f}% and 30Y {dy:+.0f}bp — "
                       "confirmed by duration. Real move.")
    return False, f"BTC {db:+.1f}% · 30Y {dy:+.0f}bp — no signal."


def level_proximity(price, sym: str) -> list[dict]:
    if not price or sym not in LEVELS:
        return []
    out = [{"level": lv, "kind": k, "dist_pct": (lv / price - 1) * 100}
           for k in ("support", "resistance") for lv in LEVELS[sym][k]]
    return sorted(out, key=lambda x: abs(x["dist_pct"]))
