"""🔧 Diagnostics — is anything actually broken, and where?"""
import pandas as pd
import streamlit as st

import core as C

st.set_page_config(page_title="Diagnostics", page_icon="🔧", layout="wide")
st.title("🔧 Diagnostics")
st.caption("If the dashboard looks blank or wrong, start here.")

if st.button("🔄 Clear cache and re-fetch everything", type="primary"):
    st.cache_data.clear()
    st.session_state.FEED_LOG = {}
    st.rerun()

st.divider()

# force every feed to run so the log is populated
with st.spinner("Probing all feeds…"):
    h = C.market()
    spot = C.crypto_spot()
    hl = C.hyperliquid_meta()
    be = C.fred("T10YIE")
    g = C.gdelt('"strait of hormuz"')
    nw = C.news("Strait of Hormuz", 3)
    pm = C.polymarket(("cpi", "fed"))

log = st.session_state.get("FEED_LOG", {})
ok = sum(1 for v in log.values() if v[0])
bad = len(log) - ok

c1, c2, c3 = st.columns(3)
c1.metric("Feeds OK", ok)
c2.metric("Feeds failing", bad, delta_color="inverse")
c3.metric("Market columns", h.shape[1] if not h.empty else 0)

if h.empty:
    st.error("**MARKET DATA COMPLETELY UNAVAILABLE.** "
             "Yahoo and Stooq both failed. On Streamlit Cloud this is usually "
             "Yahoo rate-limiting the shared IP. Wait a few minutes and press "
             "the re-fetch button, or redeploy the app to get a new IP.")
elif h.shape[1] < 8:
    st.warning(f"Partial data — only {h.shape[1]} instruments loaded. "
               "Indices will still compute but with reduced coverage.")
else:
    st.success(f"Market data healthy — {h.shape[1]} instruments, "
               f"{len(h)} rows, latest {h.index[-1]:%Y-%m-%d}.")

st.divider()
st.subheader("Feed status")
rows = [{"Feed": k, "Status": "✅ OK" if v[0] else "❌ FAIL", "Detail": v[1]}
        for k, v in sorted(log.items())]
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
a, b = st.columns(2)
with a:
    st.subheader("Key values sanity check")
    checks = []
    for name in ["US30Y", "US10Y", "BTC", "ETH", "BRENT", "DXY", "VIX"]:
        s = C.series(h, name)
        val = s.iloc[-1] if len(s) else None
        # sanity ranges — catches the /10 scaling class of bug
        rng = {"US30Y": (2, 9), "US10Y": (1, 8), "BTC": (10_000, 200_000),
               "ETH": (500, 10_000), "BRENT": (30, 200), "DXY": (80, 130),
               "VIX": (8, 90)}[name]
        if val is None:
            flag = "❌ missing"
        elif rng[0] <= val <= rng[1]:
            flag = "✅ plausible"
        else:
            flag = f"⚠️ outside {rng} — scaling bug?"
        checks.append({"Series": name,
                       "Latest": f"{val:,.2f}" if val is not None else "—",
                       "Check": flag})
    st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)

with b:
    st.subheader("Index coverage")
    dur = C.duration_stress(h, be)
    hor = C.hormuz_risk(h, g)
    st.write(f"**Duration Stress:** {dur['index']} "
             f"(built from {dur['coverage']}% of intended inputs)")
    for k, v in dur["notes"].items():
        st.caption(f"· {k}: {v}")
    st.write(f"**Chokepoint:** {hor['index']} "
             f"(built from {hor['coverage']}% of intended inputs)")
    for k, v in hor["notes"].items():
        st.caption(f"· {k}: {v}")

st.divider()
st.subheader("Crypto spot")
st.json(spot if spot else {"error": "no crypto source responded"})

st.divider()
with st.expander("Common causes of a blank dashboard"):
    st.markdown("""
| Symptom | Cause | Fix |
|---|---|---|
| Everything blank | Yahoo blocking the Streamlit Cloud IP | Press re-fetch; if it persists, redeploy (new IP). Stooq fallback should cover most of it. |
| Yields look like 0.52 instead of 5.22 | Scaling bug (%×10) | Fixed — FRED is now the primary yield source. |
| Gauges show but tape is empty | Partial feed failure | Check the table above for which one. |
| Crypto missing | CoinGecko rate limit | Binance fallback should engage automatically. |
| HYPE missing | Not on Binance under that pair | CoinGecko only — will show when it recovers. |
| Nothing updates | Cache TTL (5–30 min) | Press re-fetch above. |
""")
