"""Hormuz / war-risk: live AIS map, oil tape, filtered news, GDELT."""
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import core as C

st.set_page_config(page_title="Geopolitics & Hormuz", page_icon="🌍", layout="wide")
st.title("🌍 Geopolitics & Hormuz")

MAP_PRESETS = {
    "Strait of Hormuz (chokepoint)": (26.60, 56.40, 9),
    "Gulf of Oman (tanker queue)": (25.40, 57.80, 8),
    "Persian Gulf — full basin": (26.50, 52.50, 7),
    "Qatar / Ras Laffan LNG": (25.90, 51.60, 9),
    "Kharg Island (Iran exports)": (29.25, 50.32, 10),
    "Bab el-Mandeb (Red Sea)": (12.60, 43.30, 8),
}

h = C.market()
g = C.gdelt('"strait of hormuz" OR "iran strikes" OR "tanker attack"')
hor = C.hormuz_risk(h, g)

k = st.columns(4)
k[0].metric("CHOKEPOINT index", hor["index"] if hor["index"] is not None else "—")
for i, key in enumerate(["BRENT", "WTI", "GOLD"], start=1):
    s = h.get(C.TK[key], pd.Series(dtype=float)).dropna()
    if len(s) > 1:
        k[i].metric(key.title(), f"${s.iloc[-1]:,.2f}",
                    f"{(s.iloc[-1]/s.iloc[-2]-1)*100:+.2f}%")

st.info("**Watch threshold:** Hormuz traffic at ~30–35% of pre-war levels. "
        "CBA notes **50–60% would restore global oversupply** — that's the "
        "level where the war premium structurally deflates.")

tab_map, tab_news, tab_idx = st.tabs(["🗺️ Live AIS map", "📰 News", "📊 Components"])

with tab_map:
    a, b = st.columns([2, 1])
    view = a.selectbox("Preset view", list(MAP_PRESETS.keys()))
    prov = b.radio("Provider", ["VesselFinder", "MarineTraffic"], horizontal=True)
    lat, lon, zoom = MAP_PRESETS[view]
    if prov == "VesselFinder":
        components.html(f"""
        <div style="width:100%">
        <script type="text/javascript">
          var width="100%"; var height="600";
          var latitude="{lat}"; var longitude="{lon}";
          var zoom="{zoom}"; var names=true;
        </script>
        <script type="text/javascript"
          src="https://www.vesselfinder.com/aismap.js"></script>
        </div>""", height=620)
    else:
        components.iframe(
            f"https://www.marinetraffic.com/en/ais/embed/zoom:{zoom}/"
            f"centery:{lat}/centerx:{lon}/maptype:4/shownames:true/"
            "mmsi:0/shipid:0/fleet:0/fleet_id:0/vtypes:/showmenu:false/"
            "remember:false", height=620)
    st.caption("⚠️ **Dark ships:** in a conflict zone many vessels switch off "
               "AIS. Absence of icons ≠ absence of ships. Read with the news tab.")

with tab_news:
    KW = ["Strait of Hormuz", "Iran strike", "IRGC tanker", "Houthi tanker",
          "Oman Iran talks", "CENTCOM Iran", "oil price Iran"]
    ALERT = ["sunk", "closed", "missile", "strike", "attack", "explosion",
             "blockade", "escalat", "mine", "seiz"]
    seen, rows = set(), []
    for kw in KW:
        rows += C.news(kw, 4)
    for n in rows:
        t = n["title"].strip().lower()
        if t in seen:
            continue
        seen.add(t)
        flag = "🔴 " if any(a in t for a in ALERT) else "· "
        st.markdown(f"{flag}**[{n['title']}]({n['link']})**  \n"
                    f"<span style='opacity:.6;font-size:.8rem'>{n['pub']} · "
                    f"`{n['kw']}`</span>", unsafe_allow_html=True)

with tab_idx:
    for kk, w in hor["weights"].items():
        val = hor["components"].get(kk)
        st.progress(0 if val is None or pd.isna(val) else val,
                    text=f"**{kk}** ({int(w*100)}%) — {hor['notes'][kk]}")
    if not g.empty:
        st.subheader("GDELT news intensity")
        st.area_chart(g.set_index("date")["vol"], height=240)
    st.subheader("Oil tape")
    cols = [C.TK["BRENT"], C.TK["WTI"]]
    if all(c in h for c in cols):
        o = h[cols].dropna().tail(120)
        o.columns = ["Brent", "WTI"]
        st.line_chart(o, height=260)
