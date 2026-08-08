"""📖 Guide — plain-language explanation of everything on this dashboard."""
import streamlit as st

st.set_page_config(page_title="Guide", page_icon="📖", layout="wide")

st.title("📖 How to read this dashboard")
st.caption("Plain language. No jargon without an explanation. "
           "Start at the top and work down.")

# ------------------------------------------------------------------ 60 second
st.header("⏱️ The 60-second version")
st.markdown("""
If you only read one thing:

1. **Look at the 30Y number** on the main page. That's the 30-year US government
   bond yield. It is the single most important number here.
2. **Look at the DURATION STRESS gauge.** High (red) = bad conditions for crypto,
   no matter what the news says.
3. **Look at the red FADE banner.** If it's showing, crypto went up but bonds
   didn't agree — that rally probably won't last.
4. **Check where price sits vs the key levels** (green = support below,
   red = resistance above).

That's it. Everything else is detail.
""")

st.divider()

# ------------------------------------------------------------------ concepts
st.header("🧠 The concepts, explained simply")

with st.expander("**What is a bond yield, and why do I care?**", expanded=True):
    st.markdown("""
When you buy a government bond, you're **lending money to the US government**.
The **yield** is the interest rate they pay you.

- The **2-year yield** = lending for 2 years. Reflects what people think the
  **Fed will do in the next few meetings.**
- The **30-year yield** = lending for 30 years. Nobody lending for 30 years
  cares about the September Fed meeting. They care about one thing:
  **will my money still be worth something in 2056?**

So the 30Y is basically the market's **long-term inflation verdict**.

**Why crypto cares:** if a government bond pays you a guaranteed 5.2% per year
with no risk, then any risky asset has to beat that to be worth buying. When
the 30Y is high, crypto looks worse by comparison. When it's low, crypto looks
better. That's why we call it *crypto's discount rate*.
""")

with st.expander("**Why is crypto a 'long-duration asset'?**"):
    st.markdown("""
"Duration" just means: **how far in the future is the payoff?**

- A boring dividend stock pays you cash *today* → short duration.
- Bitcoin pays you nothing today. You own it betting it's worth much more in
  10 or 20 years → **long duration.**

Long-duration things are extremely sensitive to long-term interest rates,
because you're comparing a far-away payoff against what you could earn safely
in the meantime.

This is why, on 29 July, the selloff hit **AI infrastructure, semiconductors,
data centres — and crypto**. All the same bucket: no profits today, big promises
tomorrow.
""")

with st.expander("**What are 'payrolls' and why do they move markets?**"):
    st.markdown("""
Once a month the US government counts **how many jobs the economy added or lost**
(called *nonfarm payrolls* — they exclude farm work because it's too seasonal).

**Why it matters:** more jobs → workers are scarce → employers pay more →
people spend more → prices rise. So the jobs report is really an
**inflation report in disguise**.

**The normal logic chain:**
weak jobs → less inflation pressure → Fed doesn't need to raise rates →
cheaper money → good for crypto.

**But** — and this is the whole lesson of the last few weeks — that chain only
works *if the 30Y actually falls*. On 7 August payrolls came in **negative**
(the economy lost jobs) and Bitcoin moved barely $900, because the 30Y didn't
budge.
""")

with st.expander("**What is CPI and why is one number so important?**"):
    st.markdown("""
**CPI = Consumer Price Index.** It measures how much prices went up.

- **Headline CPI** = everything, including food and fuel.
- **Core CPI** = everything *except* food and energy.

**Why traders watch core, not headline:** oil and food prices jump around for
reasons that have nothing to do with the economy overheating (wars, weather).
Core strips that noise out and shows whether inflation is **spreading into the
rest of the economy**.

The number that matters is **core month-over-month** — how much prices rose in
that single month. A 0.1% is calm. A 0.4% is alarming.
""")

with st.expander("**What is the Fed actually doing, and what's a 'hike'?**"):
    st.markdown("""
The Federal Reserve (the Fed) sets the base interest rate for the US economy.

- **Hike** = raise rates. Makes borrowing expensive, slows the economy,
  fights inflation. **Generally bad for crypto.**
- **Cut** = lower rates. Cheap money, boosts the economy.
  **Generally good for crypto.**
- **Hold** = do nothing.

Right now the rate is **3.50–3.75%** and the Fed has held it five meetings in a
row. The debate is whether they'll *hike* next — unusual, because for years the
question was when they'd cut.

**Dovish** = leaning toward lower rates (good for risk assets).
**Hawkish** = leaning toward higher rates (bad for risk assets).
""")

with st.expander("**What is the 'term premium' / 'credibility problem'?**"):
    st.markdown("""
Normally, if inflation data comes in soft, long-term bond yields fall — the
market relaxes.

Since 29 July that **stopped happening**. Yields stayed stuck at 5.22% even
after: oil fell 25%, inflation data came in soft, and jobs went negative.

**What that means:** the bond market is saying *"we don't believe inflation is
going back to 2%, and we don't trust the Fed to force it there."* So they demand
a permanently higher yield as compensation. That extra compensation is the
**term premium**.

**Why it matters to you:** when this mindset takes hold, **good news stops
working.** Individual data points get shrugged off. That's exactly why crypto
rallies keep fizzling.
""")

with st.expander("**What is a 'bear steepener'? (the scary one)**"):
    st.markdown("""
Watch two numbers together:

| What happens | What it means | Crypto |
|---|---|---|
| 30Y ↓ and 2Y ↓ | Everything easing. Clean good news. | 🟢 rallies stick |
| 30Y ↑ and 2Y ↑ | Fed getting tougher across the board. | 🟠 pressure |
| **30Y ↑ and 2Y ↓** | **Bear steepener.** Market thinks the Fed *won't* raise rates enough, so inflation runs. | 🔴 worst case |

The third one is dangerous because it means the market has stopped trusting the
Fed. That's what happened after the July FOMC meeting.
""")

with st.expander("**What is funding rate and open interest? (Hyperliquid page)**"):
    st.markdown("""
On perpetual futures ("perps"), traders pay each other a small fee every hour
to keep the price in line with spot.

- **Funding positive** = more people betting long → longs pay shorts.
- **Funding negative** = more people betting short → shorts pay longs.
- **Open Interest (OI)** = total money in open positions.

**The rule on the dashboard:** funding above **0.05%/hour** *while OI is rising
fast* means everyone piled into the same side using borrowed money. That's
**fragile** — a small move against them triggers forced selling (liquidations)
and a cascade.

Counter-intuitively that's an **exit signal, not an entry.** When everyone
agrees, there's nobody left to buy.
""")

st.divider()

# ------------------------------------------------------------------ gauges
st.header("🎛️ The two gauges on the main page")

a, b = st.columns(2)
with a:
    st.subheader("DURATION STRESS (0–100)")
    st.markdown("""
**The question it answers:** how hostile are interest rates to crypto right now?

- **0–45 🟢** — long-term rates are calm or falling. Rallies can stick.
- **45–70 🟡** — nothing resolved. Choppy, range-bound.
- **70–100 🔴** — long end hostile. Crypto fights an uphill battle regardless
  of good news.

**What it's built from:** the 30Y level (40%), whether it's still rising (25%),
the bear-steepener check (20%), and what the market expects inflation to be (15%).

**Use it like this:** high number = trade smaller, expect rallies to fail.
""")
with b:
    st.subheader("CHOKEPOINT (0–100)")
    st.markdown("""
**The question it answers:** how much war/energy risk is priced in?

The Strait of Hormuz is a narrow sea passage where roughly **20% of the world's
oil** passes through. When it's threatened, oil spikes → inflation rises →
the Fed gets tougher → crypto suffers.

- **0–40 🟢** — calm, oil behaving.
- **40–65 🟡** — tense, headline-sensitive.
- **65–100 🔴** — active disruption priced in.

**What it's built from:** oil momentum (40%), tanker shipping stocks (25%),
defence stocks (15%), and how loudly the news is talking about it (20%).
""")

st.divider()

# ------------------------------------------------------------------ fade rule
st.header("🚫 The FADE rule — the most useful thing here")
st.markdown("""
**The rule:** if Bitcoin jumps more than 0.8% but the 30Y yield hasn't fallen,
the rally is **not confirmed**. Fade it (expect it to reverse).

**Why it works:** crypto is fast, emotional, and full of leverage. Bonds are
slow, huge, and traded by institutions with no interest in hype. When crypto
moves and bonds don't agree, the crypto move is just positioning — it fades.

**Track record since 29 July: 4 out of 4.** The 30Y ignored oil crashing 25%,
soft inflation data, negative payrolls, and the crypto bill dying. Every crypto
pop in that window faded.

The dashboard checks this automatically and shows a **red banner** when it fires.
""")

st.divider()

# ------------------------------------------------------------------ levels
st.header("📏 Support and resistance — what those numbers mean")
st.markdown("""
- **Support** = a price level below the current price where buyers have stepped
  in before. Price often bounces there. If it **breaks**, expect a faster drop
  to the next support.
- **Resistance** = a level above where sellers have appeared. Price often stalls
  there. If it **breaks convincingly**, that's a bullish signal.

**The key ones right now:**

| Coin | Watch this | Why |
|---|---|---|
| **BTC** | $63,800 | Break = drop toward $61,800 |
| **BTC** | $67,300 | Break above = genuine regime change |
| **ETH** | $2,000 | Psychological line — above it changes the picture |
| **HYPE** | **$52.48** | ⚠️ Most dangerous level here — below it triggers forced selling toward $35 |

**Important:** levels aren't magic. They tell you *where* a reaction is likely,
not *that* it will happen. Always confirm with the 30Y.
""")

st.divider()

# ------------------------------------------------------------------ routine
st.header("☀️ Your 2-minute morning routine")
st.markdown("""
Check these five things, in this order:

1. **30Y yield** — up, down, or stuck? *(main page, marked ⭐)*
2. **Duration Stress gauge** — what colour?
3. **Oil / Chokepoint** — any war escalation overnight?
4. **Where is price vs the nearest level?**
5. **Funding on Hyperliquid** — is everyone crowded on one side?

If 30Y is stuck and Duration Stress is red → **small size, fade pops, be patient.**
If 30Y is finally falling → **that's the change you've been waiting for.**
""")

st.divider()

# ------------------------------------------------------------------ mistakes
st.header("❌ The five most common mistakes")
st.markdown("""
1. **Trading the first candle after a data release.** The first 60–90 seconds
   are noise and frequently reverse. Wait 2–3 minutes. On 29 July the market
   popped mid-announcement then dropped 1,000 points.
2. **Assuming bad economic news = good for crypto.** It only works if the 30Y
   falls. Check first.
3. **Adding size into a scheduled event.** Liquidity thins right before big
   releases — your slippage gets much worse exactly when you need it not to.
4. **Chasing a move with rising funding.** If funding is spiking, you're the
   last one in.
5. **Trusting a thin prediction market.** A market with $50K volume can be moved
   by one trader. Volume matters more than the percentage.
""")

st.divider()

st.header("📚 Jargon decoder")
st.markdown("""
| Term | Plain meaning |
|---|---|
| **Hawkish** | Leaning toward higher rates. Bad for crypto. |
| **Dovish** | Leaning toward lower rates. Good for crypto. |
| **bp (basis point)** | 0.01%. "30Y rose 12bp" = rose 0.12%. |
| **m/m** | Month-over-month change. |
| **y/y** | Year-over-year change. |
| **Core** | Excluding food and energy. |
| **FOMC** | The Fed committee that sets rates. |
| **DXY** | US dollar strength index. Dollar up = crypto usually down. |
| **VIX** | Stock market fear gauge. High = scared. |
| **Term premium** | Extra yield demanded for lending long-term. |
| **Duration** | How far in the future an asset's payoff is. |
| **Liquidity** | How easily you can trade without moving the price. Thin = dangerous. |
| **Perp** | Perpetual future — a leveraged bet with no expiry date. |
| **OI** | Open Interest — total money in open positions. |
| **Consensus** | What economists on average expect. Markets react to the *surprise* vs this, not the number itself. |
""")

st.info("**The one idea to remember:** crypto's price is mostly decided by things "
        "that have nothing to do with crypto — interest rates, inflation, and oil. "
        "This dashboard exists to show you those things first, so you're not "
        "trading on the crypto chart alone.", icon="💡")

st.caption("Not investment advice. All data delayed. Levels and scenarios are "
           "planning tools, not predictions.")
