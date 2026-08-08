"""Rates deep-dive: the curve, term premium, inflation expectations."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core as C

st.set_page_config(page_title="Rates & Duration", page_icon="📉", layout="wide")
st.title("📉 Rates & Duration")
st.caption("Why this page exists: crypto is a long-duration asset. The 30Y is "
           "closer to its true discount rate than fed funds is.")

series = {k: C.fred(k) for k in C.FRED}

# ------------------------------------------------------------- headline row
cols = st.columns(5)
for i, key in enumerate(["DGS2", "DGS10", "DGS30", "T10YIE", "THREEFYTP10"]):
    df = series.get(key, pd.DataFrame())
    if not df.empty:
        last, prev = df["value"].iloc[-1], df["value"].iloc[-2]
        cols[i].metric(C.FRED[key], f"{last:.2f}%",
                       f"{(last-prev)*100:+.0f}bp", delta_color="inverse")

st.divider()

# ------------------------------------------------------------- curve
a, b = st.columns(2)
with a:
    st.subheader("The curve — 2s30s")
    d2, d30 = series.get("DGS2"), series.get("DGS30")
    if d2 is not None and not d2.empty and d30 is not None and not d30.empty:
        m = pd.merge(d2, d30, on="date", suffixes=("_2", "_30")).tail(180)
        m["spread"] = m["value_30"] - m["value_2"]
        f = go.Figure()
        f.add_trace(go.Scatter(x=m["date"], y=m["spread"], name="2s30s",
                               fill="tozeroy"))
        f.update_layout(height=300, margin=dict(t=20, b=20, l=40, r=20),
                        yaxis_title="%")
        st.plotly_chart(f, use_container_width=True)
        st.caption("**Bear steepener** (30Y up, 2Y down) = the market pricing "
                   "inflation the Fed won't contain. Worst configuration for crypto.")

with b:
    st.subheader("Inflation expectations")
    f = go.Figure()
    for key, nm in [("T10YIE", "10y breakeven"), ("T5YIFR", "5y5y forward")]:
        df = series.get(key)
        if df is not None and not df.empty:
            t = df.tail(180)
            f.add_trace(go.Scatter(x=t["date"], y=t["value"], name=nm))
    f.add_hline(y=2.0, line_dash="dot", annotation_text="Fed target")
    f.update_layout(height=300, margin=dict(t=20, b=20, l=40, r=20),
                    yaxis_title="%")
    st.plotly_chart(f, use_container_width=True)
    st.caption("If these drift up while the Fed holds, that's the credibility "
               "problem in one chart.")

st.divider()

# ------------------------------------------------------------- all yields
st.subheader("Yields — full history")
f = go.Figure()
for key, nm in [("DGS2", "2Y"), ("DGS10", "10Y"), ("DGS30", "30Y")]:
    df = series.get(key)
    if df is not None and not df.empty:
        t = df.tail(400)
        f.add_trace(go.Scatter(x=t["date"], y=t["value"], name=nm))
f.update_layout(height=380, margin=dict(t=20, b=20, l=40, r=20), yaxis_title="%")
st.plotly_chart(f, use_container_width=True)

st.divider()
st.subheader("📖 How to read this page")
st.markdown("""
| Configuration | What it means | Crypto |
|---|---|---|
| 30Y ↓ , 2Y ↓ | Clean dovish — everything easing | 🟢 rallies stick |
| 30Y ↑ , 2Y ↓ | **Bear steepener** — Fed credibility doubted | 🔴 worst case |
| 30Y ↑ , 2Y ↑ | Hawkish repricing | 🟠 pressure |
| 30Y flat on good news | Term premium entrenched | 🚫 **fade pops** |

**The 4/4 rule:** since Warsh's 29 Jul presser the 30Y has ignored oil −25%,
soft core PCE, negative payrolls and CLARITY's death. Until it moves, treat
every crypto rally as positioning rather than repricing.
""")
