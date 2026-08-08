"""Crypto desk: spot, levels, Hyperliquid funding/OI, leverage health."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core as C

st.set_page_config(page_title="Crypto & Hyperliquid", page_icon="₿", layout="wide")

if getattr(C, "VERSION", 1) < 2:
    st.error("`core.py` is out of date — replace it in the repo root and push again.")
    st.stop()
st.title("₿ Crypto & Hyperliquid")

spot = C.crypto_spot()
hl = C.hyperliquid_meta()

if not spot and hl.empty:
    st.error("No crypto data source responded (CoinGecko, Binance and "
             "Hyperliquid all failed). See 🔧 Diagnostics.")
    st.stop()
if not spot:
    st.warning("Spot feed down — showing Hyperliquid perp marks only.")

# ------------------------------------------------------------- spot + levels
cols = st.columns(3)
for i, sym in enumerate(["BTC", "ETH", "HYPE"]):
    d = spot.get(sym, {})
    px = d.get("price")
    with cols[i]:
        st.metric(sym, f"${px:,.2f}" if px else "—",
                  f"{d.get('chg'):+.2f}%" if d.get("chg") is not None else None)
        if px:
            lv = C.LEVELS[sym]
            nearest_s = max([x for x in lv["support"] if x < px], default=None)
            nearest_r = min([x for x in lv["resistance"] if x > px], default=None)
            if nearest_r:
                st.write(f"🔺 next res **{nearest_r:,}** "
                         f"({(nearest_r/px-1)*100:+.1f}%)")
            if nearest_s:
                st.write(f"🔻 next sup **{nearest_s:,}** "
                         f"({(nearest_s/px-1)*100:+.1f}%)")
            st.caption(lv["note"])

st.divider()

# ------------------------------------------------------------- HL perps
st.subheader("Hyperliquid — live perps")
if hl.empty:
    st.info("Hyperliquid API unavailable right now.")
else:
    focus = hl[hl["coin"].isin(["BTC", "ETH", "HYPE", "SOL"])]
    fc = st.columns(len(focus)) if len(focus) else []
    for i, (_, row) in enumerate(focus.iterrows()):
        health = "🟢"
        fr = row["funding"]
        if abs(fr) > 0.05:
            health = "🔴"
        elif abs(fr) > 0.02:
            health = "🟠"
        fc[i].metric(f"{health} {row['coin']}", f"${row['mark']:,.2f}",
                     f"funding {fr:+.4f}%/h")
        fc[i].caption(f"OI ${row['oi_usd']/1e6:,.0f}M · "
                      f"vol24h ${row['vol24h']/1e6:,.0f}M")

    st.markdown("**Leverage health rule:** funding >0.05%/h with OI rising "
                ">10% = leverage chasing the candle. That's an exit signal, "
                "not an entry.")

    with st.expander("All Hyperliquid perps by volume"):
        show = hl.head(30).copy()
        show["oi_usd"] = (show["oi_usd"] / 1e6).round(1)
        show["vol24h"] = (show["vol24h"] / 1e6).round(1)
        st.dataframe(
            show[["coin", "mark", "funding", "oi_usd", "vol24h"]].rename(
                columns={"mark": "Mark", "funding": "Funding %/h",
                         "oi_usd": "OI $M", "vol24h": "Vol24h $M"}),
            use_container_width=True, hide_index=True)

    # funding distribution — crowding tell
    st.subheader("Funding distribution — market-wide crowding")
    f = go.Figure(go.Histogram(x=hl["funding"].clip(-0.1, 0.1), nbinsx=40))
    f.add_vline(x=0, line_dash="dot")
    f.update_layout(height=260, margin=dict(t=20, b=20, l=40, r=20),
                    xaxis_title="funding %/hour", yaxis_title="# perps")
    st.plotly_chart(f, use_container_width=True)
    med = hl["funding"].median()
    st.caption(f"Median funding **{med:+.4f}%/h**. Strongly positive across the "
               "board = crowded longs = squeeze risk. Negative = crowded shorts.")

st.divider()

# ------------------------------------------------------------- BTC/ETH ratio
st.subheader("ETH/BTC — the pair trade")
h = C.market()
if C.data_ok(h) and C.TK["BTC"] in h and C.TK["ETH"] in h:
    r = (h[C.TK["ETH"]] / h[C.TK["BTC"]]).dropna().tail(180)
    f = go.Figure(go.Scatter(x=r.index, y=r.values, name="ETH/BTC"))
    f.update_layout(height=280, margin=dict(t=20, b=20, l=40, r=20))
    st.plotly_chart(f, use_container_width=True)
    st.caption("ETH has been the stronger leg (up ~6% on the month vs BTC flat). "
               "Long ETH / short BTC expresses the flow divergence without "
               "taking a Fed direction view.")

st.divider()
st.subheader("🎲 Crypto policy markets")
for m in C.polymarket(("clarity", "crypto", "bitcoin", "sec", "etf")):
    a, b = st.columns([1, 6])
    a.metric("YES", f"{m['yes']:.0f}%" if m["yes"] else "—")
    b.markdown(f"**[{m['q']}]({m['url']})**  \n"
               f"<span style='opacity:.6;font-size:.8rem'>24h vol "
               f"${m['vol']:,.0f}</span>", unsafe_allow_html=True)
