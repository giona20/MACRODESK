"""CPI scenario grid + countdown + live level distances."""
import datetime as dt

import pandas as pd
import streamlit as st

import core as C

st.set_page_config(page_title="CPI Battle Plan", page_icon="🎯", layout="wide")

if getattr(C, "VERSION", 1) < 2:
    st.error("`core.py` is out of date — replace it in the repo root and push again.")
    st.stop()
st.title("🎯 CPI Battle Plan")

CPI_TS = dt.datetime(2026, 8, 12, 14, 30)  # Rome
now = dt.datetime.utcnow() + dt.timedelta(hours=2)  # UTC -> CEST
delta = CPI_TS - now

if delta.total_seconds() > 0:
    d, rem = divmod(int(delta.total_seconds()), 86400)
    hh, rem = divmod(rem, 3600)
    mm = rem // 60
    st.metric("July CPI — Wed 12 Aug 14:30 Rome", f"{d}d {hh}h {mm}m")
else:
    st.success("CPI is out — score it against the grid below.")

st.info("**Consensus:** headline +0.2% m/m / ~2.8% y/y · "
        "**core +0.3% m/m / ~3.0% y/y**. June core was **0.00%**. "
        "Polymarket core-0.2% ~48.5% but only ~$50K volume — too thin to trust.")

# ---------------------------------------------------------------- grid
st.subheader("Scenario grid")
spot = C.crypto_spot()
grid = pd.DataFrame(C.CPI_GRID)
st.dataframe(
    grid.rename(columns={"print": "Core m/m", "odds": "Odds %", "tag": "",
                         "desc": "Why"}),
    use_container_width=True, hide_index=True)

st.subheader("Live distance to scenario levels")
cols = st.columns(3)
targets = {
    "BTC": {"🟢 ≤0.1%": 67300, "🟡 0.2%": 65500, "🟠 0.3%": 62500, "🔴 ≥0.4%": 57000},
    "ETH": {"🟢 ≤0.1%": 2000, "🟡 0.2%": 1975, "🟠 0.3%": 1845, "🔴 ≥0.4%": 1725},
    "HYPE": {"🟢 ≤0.1%": 60.43, "🟡 0.2%": 57.0, "🟠 0.3%": 51.14, "🔴 ≥0.4%": 47.0},
}
for i, (sym, tg) in enumerate(targets.items()):
    px = spot.get(sym, {}).get("price")
    with cols[i]:
        st.markdown(f"### {sym} — ${px:,.2f}" if px else f"### {sym}")
        for k, v in tg.items():
            if px:
                st.write(f"{k} → **{v:,}**  ({(v/px-1)*100:+.1f}%)")
            else:
                st.write(f"{k} → **{v:,}**")

st.divider()

# ---------------------------------------------------------------- execution
l, r = st.columns(2)
with l:
    st.subheader("⚡ Execution checklist")
    st.markdown("""
1. **No directional size before 14:30.** Distribution is genuinely 50/50.
2. **Don't trade the first candle.** Wait 2–3 min for the book.
3. **Confirm in order:** 30Y → 2Y → DXY → crypto.
4. **MM wide, grid/DCA paused** 14:30–14:45.
5. **Prediction markets > perps** for the directional bet (defined risk).
""")
with r:
    st.subheader("⚠️ Context")
    st.markdown("""
- **BofA bull-bear 9.7/10** — highest since 2021, explicit reduce-risk call
- **Aug–Sep** = crypto's weakest seasonal window
- **CLARITY dead** until Senate returns 11 Sep
- **Thin liquidity** = overshoots both directions
- **Asymmetry:** 30Y ignored oil −25%, soft PCE, negative payrolls (0/3).
  A soft print is worth *less* than usual; a hot one *more*.
""")

st.divider()
st.subheader("📅 Calendar")
ev = pd.DataFrame(C.EVENTS, columns=["When (Rome)", "Event", "Impact", "Why"])
st.dataframe(ev, use_container_width=True, hide_index=True)

st.divider()
st.subheader("🎲 Prediction markets — CPI & Fed")
for m in C.polymarket(("cpi", "inflation", "fed", "interest rate", "clarity")):
    a, b = st.columns([1, 6])
    a.metric("YES", f"{m['yes']:.0f}%" if m["yes"] else "—")
    b.markdown(f"**[{m['q']}]({m['url']})**  \n"
               f"<span style='opacity:.6;font-size:.8rem'>24h vol "
               f"${m['vol']:,.0f}</span>", unsafe_allow_html=True)
