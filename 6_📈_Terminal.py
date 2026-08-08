"""📈 TERMINAL — Bloomberg-style chart grid for every instrument that matters."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

import core as C

st.set_page_config(page_title="Terminal", page_icon="📈", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
html, body, [class*="css"]  { font-family:'JetBrains Mono', ui-monospace, monospace; }
.term-hdr{font-family:'JetBrains Mono',monospace;color:#00e676;font-size:1.6rem;
  font-weight:700;letter-spacing:.16em;margin-bottom:0}
.term-sub{font-family:'JetBrains Mono',monospace;color:#5c6370;font-size:.75rem;
  letter-spacing:.1em;margin-bottom:14px}
.tile{border:1px solid #1f2630;border-radius:6px;padding:8px 10px;background:#0b0e13}
.sym{color:#e8a33d;font-weight:700;font-size:.9rem;letter-spacing:.08em}
.px{color:#d7dce3;font-size:1.35rem;font-weight:700;line-height:1.15}
.up{color:#00e676}.dn{color:#ff5252}.flat{color:#8b949e}
.meta{color:#5c6370;font-size:.68rem;letter-spacing:.05em}
.bar{font-family:'JetBrains Mono',monospace;font-size:.7rem;letter-spacing:-1px}
</style>""", unsafe_allow_html=True)

st.markdown("<div class='term-hdr'>█ MACRODESK TERMINAL</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='term-sub'>LIVE TAPE · {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC · "
    "DELAYED QUOTES · FREE FEEDS</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ universe
UNIVERSE = {
    "RATES": {
        "US30Y": ("^TYX", "30Y yield ⭐ crypto's discount rate", 1),
        "US10Y": ("^TNX", "10Y yield", 1),
        "US05Y": ("^FVX", "5Y yield", 1),
    },
    "MACRO": {
        "DXY": ("DX-Y.NYB", "Dollar index — up = crypto headwind", 1),
        "VIX": ("^VIX", "Fear gauge", 1),
        "GOLD": ("GC=F", "Gold — inflation hedge", 1),
        "BRENT": ("BZ=F", "Brent crude", 1),
        "WTI": ("CL=F", "WTI crude", 1),
    },
    "EQUITY": {
        "SPX": ("^GSPC", "S&P 500 — your session anchor", 1),
        "NDX": ("^NDX", "Nasdaq 100 — long-duration proxy", 1),
    },
    "CRYPTO": {
        "BTC": ("BTC-USD", "Bitcoin", 1),
        "ETH": ("ETH-USD", "Ethereum", 1),
    },
}
FLAT = {k: v for grp in UNIVERSE.values() for k, v in grp.items()}

TFS = {
    "1D / 5m":  ("1d", "5m"),
    "5D / 15m": ("5d", "15m"),
    "1M / 1h":  ("1mo", "60m"),
    "3M / 1d":  ("3mo", "1d"),
    "6M / 1d":  ("6mo", "1d"),
    "1Y / 1d":  ("1y", "1d"),
}


@st.cache_data(ttl=300, show_spinner=False)
def ohlc(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Yahoo first; Stooq daily fallback so the terminal never goes blank."""
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         progress=False, auto_adjust=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if not df.empty:
            return _fix_scale(df, symbol)
    except Exception:
        pass
    alt = C.STOOQ.get(symbol)
    if alt:
        d = C.stooq(alt)
        if not d.empty and {"Open", "High", "Low", "Close"} <= set(d.columns):
            n = {"1d": 5, "5d": 10, "1mo": 30, "3mo": 90,
                 "6mo": 180, "1y": 365}.get(period, 120)
            return _fix_scale(d.tail(n), symbol)
    return pd.DataFrame()


def _fix_scale(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Yield tickers occasionally quote %x10 — auto-detect and correct."""
    if symbol in ("^TYX", "^TNX", "^FVX") and not df.empty:
        if float(df["Close"].iloc[-1]) > 20:
            for c in ("Open", "High", "Low", "Close"):
                if c in df:
                    df[c] = df[c] / 10
    return df


def spark(vals: list[float], width: int = 28) -> str:
    """ASCII sparkline — terminal flavour, zero dependencies."""
    blocks = "▁▂▃▄▅▆▇█"
    v = [x for x in vals if not np.isnan(x)]
    if len(v) < 2:
        return ""
    v = v[-width:]
    lo, hi = min(v), max(v)
    if hi == lo:
        return blocks[3] * len(v)
    return "".join(blocks[int((x - lo) / (hi - lo) * (len(blocks) - 1))] for x in v)


# ------------------------------------------------------------------ controls
c1, c2, c3 = st.columns([2, 2, 3])
tf_label = c1.selectbox("TIMEFRAME", list(TFS.keys()), index=3)
period, interval = TFS[tf_label]
mode = c2.selectbox("MODE", ["GRID (all)", "SINGLE (detail)"])
show_vol = c3.checkbox("Volume panel (single mode)", value=True)

st.divider()

# ------------------------------------------------------------------ ticker strip
st.markdown("<div class='term-sub'>▌ TAPE</div>", unsafe_allow_html=True)
strip = st.columns(6)
i = 0
_loaded = 0
for sym, (tkr, desc, div) in FLAT.items():
    df = ohlc(tkr, period, interval)
    if df.empty or "Close" not in df:
        continue
    s = df["Close"] / div
    last = float(s.iloc[-1])
    first = float(s.iloc[0])
    pc = (last / first - 1) * 100 if first else 0
    cls = "up" if pc > 0 else ("dn" if pc < 0 else "flat")
    arrow = "▲" if pc > 0 else ("▼" if pc < 0 else "■")
    unit = "%" if sym.startswith("US") else ""
    fmt = f"{last:,.2f}{unit}"
    with strip[i % 6]:
        st.markdown(
            f"<div class='tile'><span class='sym'>{sym}</span><br>"
            f"<span class='px'>{fmt}</span><br>"
            f"<span class='{cls}'>{arrow} {pc:+.2f}%</span><br>"
            f"<span class='bar {cls}'>{spark(s.tolist())}</span></div>",
            unsafe_allow_html=True)
    i += 1
    _loaded += 1

if _loaded == 0:
    st.error("### ⚠️ No chart data\n"
             "Yahoo and Stooq both failed. Open 🔧 Diagnostics and press "
             "*Clear cache and re-fetch*, or redeploy for a fresh IP.")
    st.stop()

st.divider()


# ------------------------------------------------------------------ chart fn
def term_chart(df: pd.DataFrame, title: str, div: float = 1,
               height: int = 300, volume: bool = False,
               hlines: list[tuple[float, str, str]] | None = None) -> go.Figure:
    o, h_, l, c = (df["Open"] / div, df["High"] / div,
                   df["Low"] / div, df["Close"] / div)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=o, high=h_, low=l, close=c, name=title,
        increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
        decreasing=dict(line=dict(color="#ff5252"), fillcolor="#ff5252")))
    # moving averages when there's room
    if len(c) > 50:
        fig.add_trace(go.Scatter(x=df.index, y=c.rolling(20).mean(),
                                 line=dict(color="#e8a33d", width=1),
                                 name="MA20"))
    if len(c) > 60:
        fig.add_trace(go.Scatter(x=df.index, y=c.rolling(50).mean(),
                                 line=dict(color="#42a5f5", width=1),
                                 name="MA50"))
    for y, lbl, col in (hlines or []):
        fig.add_hline(y=y, line_dash="dot", line_color=col, line_width=1,
                      annotation_text=lbl,
                      annotation_font=dict(size=9, color=col))
    fig.update_layout(
        template="plotly_dark", height=height,
        margin=dict(t=28, b=18, l=8, r=52),
        paper_bgcolor="#0b0e13", plot_bgcolor="#0b0e13",
        font=dict(family="JetBrains Mono, monospace", size=10, color="#8b949e"),
        title=dict(text=title, font=dict(size=12, color="#e8a33d")),
        xaxis_rangeslider_visible=False, showlegend=False,
        yaxis=dict(side="right", gridcolor="#161b22", zeroline=False),
        xaxis=dict(gridcolor="#161b22"))
    return fig


LINES = {
    "BTC": [(63800, "63.8K sup", "#ff5252"), (65135, "65.1K 50dEMA", "#e8a33d"),
            (67300, "67.3K regime", "#00e676")],
    "ETH": [(2000, "2000 line", "#00e676"), (1870, "1870 sup", "#ff5252")],
    "US30Y": [(5.22, "5.22 post-Warsh wall", "#ff5252"),
              (5.14, "5.14 unwind signal", "#00e676")],
}

# ------------------------------------------------------------------ render
if mode.startswith("GRID"):
    for group, members in UNIVERSE.items():
        st.markdown(f"<div class='term-sub'>▌ {group}</div>",
                    unsafe_allow_html=True)
        cols = st.columns(len(members) if len(members) <= 3 else 3)
        for j, (sym, (tkr, desc, div)) in enumerate(members.items()):
            df = ohlc(tkr, period, interval)
            with cols[j % len(cols)]:
                if df.empty:
                    st.warning(f"{sym}: no data")
                    continue
                st.plotly_chart(
                    term_chart(df, f"{sym}  ·  {desc}", div, 250,
                               hlines=LINES.get(sym)),
                    use_container_width=True)
        st.markdown("")
else:
    sym = st.selectbox("INSTRUMENT", list(FLAT.keys()),
                       index=list(FLAT.keys()).index("BTC"))
    tkr, desc, div = FLAT[sym]
    df = ohlc(tkr, period, interval)
    if df.empty:
        st.warning("No data for this symbol/timeframe.")
    else:
        st.plotly_chart(
            term_chart(df, f"{sym}  ·  {desc}", div, 520,
                       hlines=LINES.get(sym)), use_container_width=True)

        c = df["Close"] / div
        m = st.columns(6)
        m[0].metric("LAST", f"{c.iloc[-1]:,.2f}")
        m[1].metric("HIGH", f"{(df['High']/div).max():,.2f}")
        m[2].metric("LOW", f"{(df['Low']/div).min():,.2f}")
        m[3].metric("CHG", f"{(c.iloc[-1]/c.iloc[0]-1)*100:+.2f}%")
        rng = (df['High']/div).max() - (df['Low']/div).min()
        m[4].metric("RANGE", f"{rng:,.2f}")
        vol = c.pct_change().std() * np.sqrt(252) * 100
        m[5].metric("VOL (ann.)", f"{vol:,.1f}%" if not np.isnan(vol) else "—")

        if show_vol and "Volume" in df and df["Volume"].sum() > 0:
            fv = go.Figure(go.Bar(x=df.index, y=df["Volume"],
                                  marker_color="#2d3742"))
            fv.update_layout(template="plotly_dark", height=140,
                             margin=dict(t=8, b=18, l=8, r=52),
                             paper_bgcolor="#0b0e13", plot_bgcolor="#0b0e13",
                             font=dict(family="JetBrains Mono, monospace",
                                       size=9, color="#8b949e"),
                             yaxis=dict(side="right", gridcolor="#161b22"),
                             xaxis=dict(gridcolor="#161b22"))
            st.plotly_chart(fv, use_container_width=True)

st.divider()

# ------------------------------------------------------------------ correlation
st.markdown("<div class='term-sub'>▌ CORRELATION MATRIX · 60d daily returns</div>",
            unsafe_allow_html=True)
h = C.market()
if not h.empty:
    pick = {"BTC": C.TK["BTC"], "ETH": C.TK["ETH"], "SPX": C.TK["SPX"],
            "NDX": C.TK["NDX"], "DXY": C.TK["DXY"], "GOLD": C.TK["GOLD"],
            "BRENT": C.TK["BRENT"], "30Y": C.TK["US30Y"]}
    cols = {k: v for k, v in pick.items() if v in h.columns}
    if len(cols) > 2:
        rets = h[list(cols.values())].tail(60).pct_change().dropna()
        rets.columns = list(cols.keys())
        cm = rets.corr()
        fig = go.Figure(go.Heatmap(
            z=cm.values, x=cm.columns, y=cm.columns,
            colorscale=[[0, "#ff5252"], [.5, "#0b0e13"], [1, "#00e676"]],
            zmid=0, text=cm.round(2).values, texttemplate="%{text}",
            textfont=dict(size=10, family="JetBrains Mono, monospace")))
        fig.update_layout(template="plotly_dark", height=380,
                          margin=dict(t=10, b=10, l=10, r=10),
                          paper_bgcolor="#0b0e13", plot_bgcolor="#0b0e13",
                          font=dict(family="JetBrains Mono, monospace",
                                    size=10, color="#8b949e"))
        st.plotly_chart(fig, use_container_width=True)
        if "BTC" in cm and "NDX" in cm:
            v = cm.loc["BTC", "NDX"]
            st.caption(f"BTC↔NDX correlation **{v:.2f}**. High (>0.6) = crypto "
                       "trading as a tech proxy, not decoupled. Low/negative = "
                       "crypto running on its own flow.")

st.caption("Charts: Yahoo (delayed) with Stooq fallback. Yield scaling auto-corrected. "
           "Not investment advice.")
