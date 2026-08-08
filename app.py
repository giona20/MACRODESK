"""MACRODESK — main page. The war room."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core as C

st.set_page_config(page_title="MACRODESK", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.big-num{font-size:2.1rem;font-weight:700;line-height:1.1}
.sub{opacity:.65;font-size:.8rem}
.card{border:1px solid rgba(128,128,128,.25);border-radius:12px;padding:14px 16px;margin-bottom:10px}
</style>""", unsafe_allow_html=True)

st.title("🎯 MACRODESK")
st.caption("Duration · geopolitics · crypto policy · one screen. "
           "All free data. **New here? Open 📖 Guide in the sidebar.**")

with st.spinner("Loading feeds…"):
    h = C.market()
    be = C.fred("T10YIE")
    spot = C.crypto_spot()
    g = C.gdelt('"strait of hormuz" OR "iran strikes" OR "tanker attack"')

# ---------------------------------------------------------------- health gate
if not C.data_ok(h) and not spot:
    st.error("### ⚠️ No data loaded\n"
             "Every market feed failed. This is almost always Yahoo "
             "rate-limiting the Streamlit Cloud IP.\n\n"
             "**Open the 🔧 Diagnostics page** (sidebar) and press "
             "*Clear cache and re-fetch*. If it persists, redeploy the app.")
    st.stop()

if not C.data_ok(h):
    st.warning("Partial data: market history unavailable, showing crypto only. "
               "See 🔧 Diagnostics.")

dur = C.duration_stress(h, be)
hor = C.hormuz_risk(h, g)
label, color, advice = C.regime(dur["index"], hor["index"])
fade, fade_msg = C.fade_rule(h)

if dur["coverage"] < 60 or hor["coverage"] < 60:
    st.info(f"Indices built from partial inputs "
            f"(duration {dur['coverage']}%, chokepoint {hor['coverage']}%). "
            "See 🔧 Diagnostics for which feed is down.")

with st.expander("❓ What am I looking at? (30-second version)"):
    st.markdown("""
- **DURATION STRESS** — how hostile interest rates are to crypto.
  Red = rallies tend to fail no matter what the news says.
- **CHOKEPOINT** — how much war/oil risk is priced in.
- **30Y ⭐** — the 30-year bond yield. The most important number here:
  effectively crypto's discount rate. Stuck or rising = headwind.
- **Red FADE banner** — crypto rose but bonds didn't agree. The move likely
  won't last.

Full explanations in **📖 Guide** (sidebar).
""")

if fade:
    st.error(f"🚫 **FADE SIGNAL** — {fade_msg}")
else:
    st.info(f"**30Y confirmation check** — {fade_msg}")

c1, c2, c3 = st.columns([1.1, 1.1, 1.6])
with c1:
    f = go.Figure(go.Indicator(
        mode="gauge+number", value=dur["index"] or 0,
        title={"text": "DURATION STRESS", "font": {"size": 14}},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": color},
               "steps": [{"range": [0, 45], "color": "#e8f5e9"},
                         {"range": [45, 70], "color": "#fff8e1"},
                         {"range": [70, 100], "color": "#ffebee"}]}))
    f.update_layout(height=200, margin=dict(t=40, b=5, l=25, r=25))
    st.plotly_chart(f, use_container_width=True)
with c2:
    f = go.Figure(go.Indicator(
        mode="gauge+number", value=hor["index"] or 0,
        title={"text": "CHOKEPOINT (war/oil)", "font": {"size": 14}},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#455a64"},
               "steps": [{"range": [0, 40], "color": "#e8f5e9"},
                         {"range": [40, 65], "color": "#fff8e1"},
                         {"range": [65, 100], "color": "#ffebee"}]}))
    f.update_layout(height=200, margin=dict(t=40, b=5, l=25, r=25))
    st.plotly_chart(f, use_container_width=True)
with c3:
    st.markdown(f"<div class='card'><div class='sub'>REGIME</div>"
                f"<div class='big-num' style='color:{color}'>{label}</div>"
                f"<div style='margin-top:6px'>{advice}</div></div>",
                unsafe_allow_html=True)

# ---------------------------------------------------------------- tape
st.subheader("The tape")
k = st.columns(6)
tape = [("30Y ⭐", "US30Y", "%", True), ("10Y", "US10Y", "%", True),
        ("DXY", "DXY", "", False), ("Brent", "BRENT", "$", False),
        ("Gold", "GOLD", "$", False), ("VIX", "VIX", "", False)]
for i, (name, key, unit, is_yield) in enumerate(tape):
    s = C.series(h, key)
    if len(s) < 2:
        k[i].metric(name, "—", help="feed down — see Diagnostics")
        continue
    last, prev = s.iloc[-1], s.iloc[-2]
    if is_yield:
        k[i].metric(name, f"{last:.2f}%", f"{(last-prev)*100:+.0f}bp",
                    delta_color="inverse",
                    help="THE indicator — crypto's discount rate" if key == "US30Y" else None)
    else:
        pre = unit if unit == "$" else ""
        k[i].metric(name, f"{pre}{last:,.2f}", f"{(last/prev-1)*100:+.2f}%")

st.divider()

# ---------------------------------------------------------------- crypto
st.subheader("Crypto vs key levels")
cc = st.columns(3)
for i, sym in enumerate(["BTC", "ETH", "HYPE"]):
    d = spot.get(sym, {})
    px = d.get("price")
    with cc[i]:
        st.metric(sym, f"${px:,.2f}" if px else "—",
                  f"{d.get('chg'):+.2f}%" if d.get("chg") is not None else None)
        st.caption(C.LEVELS[sym]["note"])
        for lv in C.level_proximity(px, sym)[:3]:
            arrow = "🔺" if lv["kind"] == "resistance" else "🔻"
            st.markdown(f"<span class='sub'>{arrow} {lv['kind'][:3]} "
                        f"**{lv['level']:,}** &nbsp; {lv['dist_pct']:+.1f}%</span>",
                        unsafe_allow_html=True)

st.divider()
a, b = st.columns(2)
with a:
    st.subheader("Duration stress breakdown")
    for kk, w in dur["weights"].items():
        v = dur["components"].get(kk, np.nan)
        st.progress(0 if (v is None or np.isnan(v)) else v,
                    text=f"**{kk}** ({int(w*100)}%) — {dur['notes'][kk]}")
    st.caption("High = long end hostile to risk assets. This is what actually "
               "prices crypto, not the next Fed meeting.")
with b:
    st.subheader("Chokepoint breakdown")
    for kk, w in hor["weights"].items():
        v = hor["components"].get(kk, np.nan)
        st.progress(0 if (v is None or np.isnan(v)) else v,
                    text=f"**{kk}** ({int(w*100)}%) — {hor['notes'][kk]}")

y30 = C.series(h, "US30Y")
if len(y30):
    st.subheader("30Y yield — the spine")
    f = go.Figure(go.Scatter(x=y30.index, y=y30.values, name="30Y",
                             line=dict(width=2)))
    f.add_hline(y=5.22, line_dash="dot", annotation_text="5.22 post-Warsh wall")
    f.add_hline(y=5.14, line_dash="dot", line_color="green",
                annotation_text="5.14 pre-presser (unwind signal)")
    f.update_layout(height=300, margin=dict(t=20, b=20, l=40, r=20),
                    yaxis_title="%")
    st.plotly_chart(f, use_container_width=True)

st.caption("MACRODESK · free-data build · delayed quotes · not investment advice")
"""MACRODESK — main page. The war room."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core as C

st.set_page_config(page_title="MACRODESK", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.big-num{font-size:2.1rem;font-weight:700;line-height:1.1}
.sub{opacity:.65;font-size:.8rem}
.card{border:1px solid rgba(128,128,128,.25);border-radius:12px;padding:14px 16px;margin-bottom:10px}
</style>""", unsafe_allow_html=True)

st.title("🎯 MACRODESK")
st.caption("Duration · geopolitics · crypto policy · one screen. "
           "All free data. **New here? Open 📖 Guide in the sidebar.**")

with st.spinner("Loading feeds…"):
    h = C.market()
    be = C.fred("T10YIE")
    spot = C.crypto_spot()
    g = C.gdelt('"strait of hormuz" OR "iran strikes" OR "tanker attack"')

# ---------------------------------------------------------------- health gate
if not C.data_ok(h) and not spot:
    st.error("### ⚠️ No data loaded\n"
             "Every market feed failed. This is almost always Yahoo "
             "rate-limiting the Streamlit Cloud IP.\n\n"
             "**Open the 🔧 Diagnostics page** (sidebar) and press "
             "*Clear cache and re-fetch*. If it persists, redeploy the app.")
    st.stop()

if not C.data_ok(h):
    st.warning("Partial data: market history unavailable, showing crypto only. "
               "See 🔧 Diagnostics.")

dur = C.duration_stress(h, be)
hor = C.hormuz_risk(h, g)
label, color, advice = C.regime(dur["index"], hor["index"])
fade, fade_msg = C.fade_rule(h)

if dur["coverage"] < 60 or hor["coverage"] < 60:
    st.info(f"Indices built from partial inputs "
            f"(duration {dur['coverage']}%, chokepoint {hor['coverage']}%). "
            "See 🔧 Diagnostics for which feed is down.")

with st.expander("❓ What am I looking at? (30-second version)"):
    st.markdown("""
- **DURATION STRESS** — how hostile interest rates are to crypto.
  Red = rallies tend to fail no matter what the news says.
- **CHOKEPOINT** — how much war/oil risk is priced in.
- **30Y ⭐** — the 30-year bond yield. The most important number here:
  effectively crypto's discount rate. Stuck or rising = headwind.
- **Red FADE banner** — crypto rose but bonds didn't agree. The move likely
  won't last.

Full explanations in **📖 Guide** (sidebar).
""")

if fade:
    st.error(f"🚫 **FADE SIGNAL** — {fade_msg}")
else:
    st.info(f"**30Y confirmation check** — {fade_msg}")

c1, c2, c3 = st.columns([1.1, 1.1, 1.6])
with c1:
    f = go.Figure(go.Indicator(
        mode="gauge+number", value=dur["index"] or 0,
        title={"text": "DURATION STRESS", "font": {"size": 14}},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": color},
               "steps": [{"range": [0, 45], "color": "#e8f5e9"},
                         {"range": [45, 70], "color": "#fff8e1"},
                         {"range": [70, 100], "color": "#ffebee"}]}))
    f.update_layout(height=200, margin=dict(t=40, b=5, l=25, r=25))
    st.plotly_chart(f, use_container_width=True)
with c2:
    f = go.Figure(go.Indicator(
        mode="gauge+number", value=hor["index"] or 0,
        title={"text": "CHOKEPOINT (war/oil)", "font": {"size": 14}},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#455a64"},
               "steps": [{"range": [0, 40], "color": "#e8f5e9"},
                         {"range": [40, 65], "color": "#fff8e1"},
                         {"range": [65, 100], "color": "#ffebee"}]}))
    f.update_layout(height=200, margin=dict(t=40, b=5, l=25, r=25))
    st.plotly_chart(f, use_container_width=True)
with c3:
    st.markdown(f"<div class='card'><div class='sub'>REGIME</div>"
                f"<div class='big-num' style='color:{color}'>{label}</div>"
                f"<div style='margin-top:6px'>{advice}</div></div>",
                unsafe_allow_html=True)

# ---------------------------------------------------------------- tape
st.subheader("The tape")
k = st.columns(6)
tape = [("30Y ⭐", "US30Y", "%", True), ("10Y", "US10Y", "%", True),
        ("DXY", "DXY", "", False), ("Brent", "BRENT", "$", False),
        ("Gold", "GOLD", "$", False), ("VIX", "VIX", "", False)]
for i, (name, key, unit, is_yield) in enumerate(tape):
    s = C.series(h, key)
    if len(s) < 2:
        k[i].metric(name, "—", help="feed down — see Diagnostics")
        continue
    last, prev = s.iloc[-1], s.iloc[-2]
    if is_yield:
        k[i].metric(name, f"{last:.2f}%", f"{(last-prev)*100:+.0f}bp",
                    delta_color="inverse",
                    help="THE indicator — crypto's discount rate" if key == "US30Y" else None)
    else:
        pre = unit if unit == "$" else ""
        k[i].metric(name, f"{pre}{last:,.2f}", f"{(last/prev-1)*100:+.2f}%")

st.divider()

# ---------------------------------------------------------------- crypto
st.subheader("Crypto vs key levels")
cc = st.columns(3)
for i, sym in enumerate(["BTC", "ETH", "HYPE"]):
    d = spot.get(sym, {})
    px = d.get("price")
    with cc[i]:
        st.metric(sym, f"${px:,.2f}" if px else "—",
                  f"{d.get('chg'):+.2f}%" if d.get("chg") is not None else None)
        st.caption(C.LEVELS[sym]["note"])
        for lv in C.level_proximity(px, sym)[:3]:
            arrow = "🔺" if lv["kind"] == "resistance" else "🔻"
            st.markdown(f"<span class='sub'>{arrow} {lv['kind'][:3]} "
                        f"**{lv['level']:,}** &nbsp; {lv['dist_pct']:+.1f}%</span>",
                        unsafe_allow_html=True)

st.divider()
a, b = st.columns(2)
with a:
    st.subheader("Duration stress breakdown")
    for kk, w in dur["weights"].items():
        v = dur["components"].get(kk, np.nan)
        st.progress(0 if (v is None or np.isnan(v)) else v,
                    text=f"**{kk}** ({int(w*100)}%) — {dur['notes'][kk]}")
    st.caption("High = long end hostile to risk assets. This is what actually "
               "prices crypto, not the next Fed meeting.")
with b:
    st.subheader("Chokepoint breakdown")
    for kk, w in hor["weights"].items():
        v = hor["components"].get(kk, np.nan)
        st.progress(0 if (v is None or np.isnan(v)) else v,
                    text=f"**{kk}** ({int(w*100)}%) — {hor['notes'][kk]}")

y30 = C.series(h, "US30Y")
if len(y30):
    st.subheader("30Y yield — the spine")
    f = go.Figure(go.Scatter(x=y30.index, y=y30.values, name="30Y",
                             line=dict(width=2)))
    f.add_hline(y=5.22, line_dash="dot", annotation_text="5.22 post-Warsh wall")
    f.add_hline(y=5.14, line_dash="dot", line_color="green",
                annotation_text="5.14 pre-presser (unwind signal)")
    f.update_layout(height=300, margin=dict(t=20, b=20, l=40, r=20),
                    yaxis_title="%")
    st.plotly_chart(f, use_container_width=True)

st.caption("MACRODESK · free-data build · delayed quotes · not investment advice")
