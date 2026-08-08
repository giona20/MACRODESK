"""📖 Guide — plain-language explanation of everything. No prior knowledge assumed."""
import streamlit as st

st.set_page_config(page_title="Guide", page_icon="📖", layout="wide")

st.title("📖 The Guide")
st.caption("Everything on this dashboard, explained from zero. "
           "No jargon without a translation.")

tabs = st.tabs([
    "🚀 Start here", "🧠 Core concepts", "📊 Data releases",
    "🏛️ The Fed", "🌍 War & oil", "₿ Crypto mechanics",
    "🎛️ The gauges", "📈 Reading charts", "☀️ Daily routine", "📚 Dictionary",
])

# ════════════════════════════════════════════════════ START HERE
with tabs[0]:
    st.header("The 60-second version")
    st.markdown("""
If you read nothing else:

1. **Look at the 30Y number** on the main page (marked ⭐). It's the 30-year US
   government bond yield. It's the most important number here.
2. **Look at the DURATION STRESS gauge.** Red = bad conditions for crypto,
   regardless of what the news says.
3. **Look for the red FADE banner.** If it's showing, crypto went up but bonds
   didn't agree — that rally probably won't hold.
4. **Check price vs the key levels.** Green = support below, red = resistance above.

Everything else is detail.
""")

    st.header("The one big idea")
    st.info("""
**Crypto's price is mostly decided by things that have nothing to do with crypto.**

Interest rates, inflation and oil move Bitcoin more than anything happening
inside crypto itself. That's why this dashboard shows you bonds and oil *before*
a crypto chart. If you only watch the crypto chart, you're watching the shadow
instead of the thing casting it.
""", icon="💡")

    st.header("The chain of causation (memorise this)")
    st.markdown("""
This is how it all connects. Read top to bottom:

```
WAR IN THE MIDDLE EAST
        ↓
   OIL PRICE UP
        ↓
   INFLATION UP     (fuel is in everything: transport, food, factories)
        ↓
FED KEEPS RATES HIGH  to fight inflation
        ↓
   BOND YIELDS UP   (safe investments now pay more)
        ↓
 RISKY ASSETS DOWN  (why gamble on crypto if bonds pay 5% guaranteed?)
        ↓
    BTC / ETH DOWN
```

Every measurement on this dashboard is one link in that chain. It runs in
reverse too: **oil falls → inflation cools → yields fall → crypto rallies.**
""")

    st.header("The three coins tracked here")
    st.markdown("""
| Coin | What it is | Behaviour |
|---|---|---|
| **BTC** | Bitcoin — the benchmark | Moves most with macro |
| **ETH** | Ethereum | Higher beta — bigger swings both ways |
| **HYPE** | Hyperliquid's token | Highest beta of the three |

**"Beta"** = how much an asset amplifies the market's move. If BTC rises 5% and
HYPE rises 12%, HYPE is high beta. Great upward, brutal downward.
""")

# ════════════════════════════════════════════════════ CONCEPTS
with tabs[1]:
    st.header("🧠 Core concepts")

    with st.expander("**What is a bond, and what is a 'yield'?**", expanded=True):
        st.markdown("""
Buying a **government bond** means lending money to the US government. They pay
interest, then return your money at the end.

The **yield** is the interest rate you earn.

- **2-year yield** = lending for 2 years → reflects **what the Fed does soon**
- **30-year yield** = lending for 30 years → nobody lending for three decades
  cares about the next Fed meeting. They care about **"will my money be worth
  anything in 2056?"**

So the 30Y is the market's **long-term inflation verdict**.

**Key insight:** government bonds are treated as risk-free. So their yield is the
**bar every other investment must beat.** If bonds pay 5.2% guaranteed, a risky
asset with no income has to promise a lot more to be worth owning.
""")

    with st.expander("**Why is the 30Y called 'crypto's discount rate'?**"):
        st.markdown("""
A **discount rate** answers: *how much is future money worth today?*

High rates → future money is worth **less** today (you could have earned that
high rate instead). Low rates → future money is worth **more**.

Bitcoin pays nothing today. Its entire value is a bet on the future. So it's
extremely sensitive to what future money is worth — which long-term rates set.

- 30Y at **5.2%** → future payoffs heavily discounted → crypto looks expensive
- 30Y at **3.5%** → future payoffs barely discounted → crypto looks cheap

That's why the 30Y is closer to crypto's true discount rate than the Fed's own
policy rate is.
""")

    with st.expander("**What does 'long-duration asset' mean?**"):
        st.markdown("""
**Duration = how far in the future is the payoff?**

| Asset | Payoff arrives | Duration | Rate sensitivity |
|---|---|---|---|
| Cash / savings | Now | ~zero | None |
| Dividend stock | Every quarter | Short | Low |
| Growth tech stock | Profits in 10 yrs | Long | High |
| **Bitcoin** | A bet on 2040 | **Very long** | **Very high** |

This is why on 29 July the selloff hit **AI infrastructure, semiconductors, data
centres — and crypto.** Same bucket: no profits today, big promises tomorrow.
They reprice together when long rates move.

It also explains something that confuses people: why crypto often follows tech
stocks rather than gold. In practice it is **not** a safe haven — it's a
long-duration risk asset.
""")

    with st.expander("**Term premium and the 'credibility problem'**"):
        st.markdown("""
**Normally:** soft inflation data → long yields fall → relief.

**Since 29 July that stopped working.** Yields stayed pinned near 5.22% even
after oil crashed 25%, inflation data came in soft, jobs went **negative**, and
the crypto bill died.

**What that means:** the bond market is saying *"we don't believe inflation is
returning to 2%, and we don't trust the Fed to force it."* So investors demand
extra compensation to lend long-term. That extra is the **term premium**.

**Why it beats any single data point:** once this mindset sets in, **good news
stops working.** The market has pre-committed to a view. That's precisely why
crypto rallies keep fizzling — and it's the most important thing to understand
about the current market.
""")

    with st.expander("**What is a 'bear steepener'? (the dangerous one)**"):
        st.markdown("""
Watch the 2Y and 30Y **together**:

| 2Y | 30Y | Name | Meaning | Crypto |
|---|---|---|---|---|
| ↓ | ↓ | Everything easing | Clean good news | 🟢 rallies stick |
| ↑ | ↑ | Parallel shift up | Fed tougher across the board | 🟠 pressure |
| ↓ | **↑** | **BEAR STEEPENER** | Market thinks Fed **won't** tighten enough → inflation runs | 🔴 **worst** |
| ↑ | ↓ | Flattener | Tightening into a slowdown | 🟠 recession signal |

**Why the bear steepener is scary:** the short end falling says *"the Fed won't
hike."* The long end rising says *"and that's a mistake — inflation is coming."*
It's the bond market openly disagreeing with the central bank.

Exactly what happened after the July FOMC: 30Y **+12bp to 5.21%** (19-year high)
while the 2Y **fell 4bp**.
""")

    with st.expander("**What does 'priced in' mean?**"):
        st.markdown("""
Markets move on **surprise**, not on news.

If everyone expects a hold and the Fed holds — **nothing happens.** The price
already reflected it. It was "priced in."

**This is the most common beginner mistake:** seeing good news and wondering why
price didn't move. The answer is everyone already knew.

**How to use it:**
1. Before any release, find the **consensus** (what economists expect)
2. Compare to the actual number
3. **The gap is what moves price**

A hold priced at 70% isn't bullish when it happens. A hike priced at 30% is a
shock — 70% of the market must reposition at once.
""")

    with st.expander("**Asymmetry — how professionals actually think**"):
        st.markdown("""
Asymmetry = **the upside and downside aren't equal.**

The real example from this market:

The 30Y ignored *four* pieces of good news in a row. Therefore:
- **More good news** → probably ignored again → **small upside**
- **Bad news** → **confirms** what bonds already suspect → **big downside**

Confirmation of an existing fear moves prices more than a challenge to it. So
risk is **skewed to the downside** even if the odds are 50/50.

**The flip side:** if the "impossible" good outcome *does* land, nobody is
positioned for it, so everyone repositions at once — and that move is enormous.

**The professional's question isn't "what's most likely?" It's "what's the
payoff if I'm right versus the cost if I'm wrong?"**
""")

# ════════════════════════════════════════════════════ DATA
with tabs[2]:
    st.header("📊 The data releases that move markets")

    with st.expander("**PAYROLLS (jobs report) — first Friday of the month**",
                     expanded=True):
        st.markdown("""
**What it is:** the government surveys employers and counts jobs added or lost.
Called **nonfarm payrolls** (farm work is excluded — too seasonal to be useful).

**Why markets care:** more jobs → workers scarce → employers pay more → people
spend more → **prices rise.** The jobs report is really an **inflation report in
disguise.**

**The four numbers released together:**

| Number | Meaning |
|---|---|
| **Payrolls** | Jobs added/lost — the headline |
| **Unemployment rate** | % looking for work who can't find it |
| **Average Hourly Earnings** | Wage growth. **Often matters more than the headline** |
| **Participation rate** | % of adults in the workforce at all |

**⚠️ The trap — a falling unemployment rate can be bad news.**

The unemployment rate only counts people **actively looking**. If people give up
and stop looking, they vanish from the count and unemployment **falls even
though things got worse.**

Exactly what happened on 7 August: unemployment fell to 4.1% (looks great) but
**participation dropped to 61.4%** — people left the workforce. Payrolls were
**−23,000**: the economy actually *lost* jobs.

**Always check participation before believing the unemployment rate.**
""")

    with st.expander("**CPI (inflation) — around the 12th of each month**"):
        st.markdown("""
**CPI = Consumer Price Index.** How much prices rose.

- **Headline CPI** = everything, including food and fuel
- **Core CPI** = everything **except** food and energy

**Why traders watch core:** oil and food jump for reasons unrelated to the
economy overheating — wars, weather, harvests. Core strips that out and shows
whether inflation is **spreading into the rest of the economy.** That's what the
Fed responds to.

**The number that matters: core month-over-month.**

| Print | Reading |
|---|---|
| 0.0–0.1% | Very calm — inflation basically stopped |
| 0.2% | Normal / acceptable |
| 0.3% | Uncomfortable — annualises to ~3.6% |
| 0.4%+ | Alarming — the Fed must act |

**Why the current print is loaded:** June core was **0.00%** (flat). The July
print is the first data containing the oil spike. If core stays low despite oil,
the shock never spread. If it jumps, passthrough is real.

**Inside the report, check:** *shelter* (housing, ~⅓ of core) and *supercore*
(core services excluding housing — the Fed's favourite persistence gauge).
""")

    with st.expander("**PCE — the Fed's actual target**"):
        st.markdown("""
Something that confuses almost everyone: **the Fed does not target CPI.**

They target **PCE** (Personal Consumption Expenditures price index). The famous
"2% target" is 2% on *PCE*.

**Difference:** PCE covers more, weights differently (less housing-heavy) and
adjusts for people substituting cheaper goods. It usually runs **lower** than CPI.

**Why watch both:** CPI comes out first, so it moves markets. PCE is what the
Fed actually decides on. When they diverge, that gap is information.
""")

    with st.expander("**GDP — the growth number**"):
        st.markdown("""
**GDP = total value of everything the economy produced.** Reported as an
**annualised quarterly rate** (if this quarter's pace continued all year, growth
would be X%).

Three versions release a month apart — the **advance** estimate moves markets.

**Hidden gem inside it: the GDP price index (deflator).** The broadest inflation
measure that exists — the *entire economy*, not a consumer basket. On 30 July it
printed **6.3%** vs 3.7% prior. Almost nobody watches it, but it's a big part of
why bonds refused to rally.
""")

    with st.expander("**JOBLESS CLAIMS — every Thursday**"):
        st.markdown("""
People filing for unemployment benefits for the **first time** last week. The
highest-frequency labour data available.

**Scale:** ~200k healthy · >250k softening · <200k very tight

**Continuing claims** = people *still* receiving benefits. Rising continuing
claims with flat initial claims means **people aren't getting rehired** — a
subtler, often earlier warning sign.
""")

    with st.expander("**PMI / ISM — the survey numbers**"):
        st.markdown("""
Surveys asking purchasing managers: is business better or worse than last month?

**The scale: 50 is the dividing line.** Above = expanding. Below = contracting.

- **Manufacturing PMI** — factories
- **Services PMI** — ~70% of the US economy, so more important
- **"Flash" PMI** — early preliminary read on the *current* month

**⭐ The part to actually watch: the "prices paid" sub-index.** It asks whether
input costs are rising — a **real-time inflation preview weeks before CPI.** On
24 July it showed the steepest selling-price inflation in nearly four years, a
warning that predated the data.
""")

# ════════════════════════════════════════════════════ FED
with tabs[3]:
    st.header("🏛️ The Fed — who they are, what they do")
    st.markdown("""
The **Federal Reserve** is the US central bank. It sets the base interest rate
that everything else in finance prices off.

The deciding committee is the **FOMC** — 12 voting members, 8 meetings a year.
Current Chair: **Kevin Warsh**.
""")

    with st.expander("**Hike, cut, hold**", expanded=True):
        st.markdown("""
| Action | Effect | Crypto |
|---|---|---|
| **HIKE** | Raises rates. Borrowing expensive, economy slows | 🔴 Bad |
| **CUT** | Lowers rates. Cheap money, stimulus | 🟢 Good |
| **HOLD** | No change | Depends what was expected |

**Current:** rate is **3.50–3.75%**, held five straight meetings. The debate is
whether they'll **hike** — unusual, since for years the question was when they'd
cut.

**Two words you'll see constantly:**
- **Hawkish** 🦅 = leaning toward higher rates → bad for risk assets
- **Dovish** 🕊️ = leaning toward lower rates → good for risk assets
""")

    with st.expander("**How an FOMC day actually works**"):
        st.markdown("""
**20:00 Rome — the statement.** A short document. Traders compare it
**word-for-word against the previous one** — the *changes* are the message.

**20:00–20:05 — the knee-jerk.** Algorithms react in milliseconds. **This move
is frequently wrong and gets reversed.**

**20:30 — the press conference.** The Chair takes questions. **This is where the
meeting is actually decided** — the reversal usually happens here.

**⚠️ Real example:** on 29 July the market briefly rose *during* the press
conference, then closed **down 1,000 points on the Dow.** Anyone trading the
first candle got run over.
""")

    with st.expander("**Dissents — the highest-information item**"):
        st.markdown("""
FOMC decisions are voted on. Usually everyone agrees. A member voting against is
a **dissent**.

**Why it matters:** it reveals the committee is split and shows which direction
the argument is heading for *next* time.

**Real example:** June's vote was **12–0**, unanimous. July's was **9–3** —
Hammack, Logan and Kashkari all voted for a **hike**. The most same-direction
dissents since 2016, and a loud signal the hawkish camp is mobilising.
""")

    with st.expander("**What is the 'dot plot'?**"):
        st.markdown("""
Four times a year each Fed member anonymously marks where they think rates will
be in future years. Each dot = one member.

**Why it matters:** it's the closest thing to the Fed publishing its plan.

**When there's no dot plot** (like July's meeting), the Chair's press conference
is the *only* forward guidance — which makes his exact wording enormous.
""")

    with st.expander("**How do I see what the market expects?**"):
        st.markdown("""
**CME FedWatch** (free — search for it). It converts futures prices into
probabilities: "70% hold, 30% hike."

**How to use it:**
1. Check odds **before** the decision
2. Compare with what happens
3. **The gap moves price**

Remember: a 70%-expected hold is not bullish when it arrives.
""")

# ════════════════════════════════════════════════════ WAR
with tabs[4]:
    st.header("🌍 War, oil, and why a strait moves Bitcoin")

    with st.expander("**What is the Strait of Hormuz?**", expanded=True):
        st.markdown("""
A narrow sea passage between Iran and Oman — about **21 miles wide** at its
tightest. Roughly **20% of the world's oil** passes through it.

**Why it's the most important geography in finance:** if it closes, a fifth of
global oil supply is stuck. Prices spike immediately.

```
Strait threatened → oil up → petrol, transport, food cost more
→ inflation up → Fed stays tough → yields up → crypto down
```

That's why a naval standoff thousands of miles away changes your Bitcoin
position. Not coincidence — causation.
""")

    with st.expander("**Why does oil affect inflation so much?**"):
        st.markdown("""
Energy is only ~8% of the consumer basket directly. But it's an **input to
nearly everything**:

- Every product is **transported** (fuel)
- Food is **grown and shipped** using fuel and fuel-based fertiliser
- Factories run on **energy**
- Plastics are literally **made from oil**

So an oil spike seeps into everything over time. Economists call this
**passthrough**.

**The critical question right now:** did July's oil spike stay contained in
energy prices, or pass through into core inflation? That's exactly what the CPI
print answers.
""")

    with st.expander("**Stagflation — why it's the worst case**"):
        st.markdown("""
**Stagflation = stagnant growth + high inflation simultaneously.**

Normally these move oppositely — a weak economy has weak demand and low
inflation. Stagflation breaks that, usually via a **supply shock** (an oil
crisis): things get expensive because supply is *blocked*, not because demand is
strong.

**Why it's the worst case:** the Fed has no good move.
- Cut rates to help growth → inflation worsens
- Raise rates to fight inflation → crushes a weak economy

**The tell:** normally weak data is *good* for risk assets (the Fed will ease).
In stagflation that reflex **breaks** — bad news is just bad news.

**⭐ Your practical signal: if the 10Y or 30Y RISES on a weak data print, the
"bad news is good news" reflex is broken.** Don't buy that dip.
""")

    with st.expander("**Reading the AIS ship map**"):
        st.markdown("""
The Geopolitics page shows **live ship positions** (AIS = the transponder system
ships broadcast from).

**What to look for:**
- **Healthy strait:** continuous two-lane tanker stream moving through
- **Blocked:** empty strait, ships **clustered in the Gulf of Oman** waiting
- **Kharg Island empty** = Iranian oil exports stopped

**⚠️ "Dark ships":** in a conflict zone many vessels (especially sanctioned
"shadow fleet" tankers) **switch transponders off.** An empty map does **not**
mean an empty sea. Read it with the news tab, never alone.

**The threshold:** traffic is ~30–35% of pre-war levels. Analysts say
**50–60% would restore global oversupply** — the level where the war premium
structurally deflates.
""")

# ════════════════════════════════════════════════════ CRYPTO
with tabs[5]:
    st.header("₿ Crypto mechanics")

    with st.expander("**What is a perpetual future ('perp')?**", expanded=True):
        st.markdown("""
A **perp** is a bet on a coin's price that never expires and lets you use
**leverage** (borrowed money).

**Example:** with $1,000 at 10× leverage you control $10,000 of Bitcoin. A 10%
move your way doubles your money. A 10% move against you **wipes you out** —
that's a **liquidation**.

**Why the dashboard tracks this:** when many people use leverage in the same
direction, a small move triggers **forced selling**, which pushes price further,
triggering more forced selling. That's a **liquidation cascade** — why crypto
drops are so violent.
""")

    with st.expander("**Funding rate — the crowding detector**"):
        st.markdown("""
Since perps never expire, they need a mechanism to stay tied to the real price:
the **funding rate**, a small fee paid hourly between longs and shorts.

- **Positive** = too many longs → longs pay shorts
- **Negative** = too many shorts → shorts pay longs

| Funding | Meaning | Action |
|---|---|---|
| Near 0 | Balanced | Normal |
| Slightly + | Mild bullish lean | Fine |
| **>0.05%/h with OI rising** | Crowded longs on borrowed money | 🔴 **Exit signal** |
| Strongly negative | Crowded shorts | Upward squeeze risk |

**The counter-intuitive lesson: when everyone agrees, there's nobody left to
buy.** Extreme funding is a warning, not a confirmation.
""")

    with st.expander("**Open Interest (OI)**"):
        st.markdown("""
**OI = total value of all open positions.**

- **Rising OI + rising price** = new money entering (healthy)
- **Rising OI + high funding** = leverage chasing the move (fragile)
- **Falling OI + big move** = positions closing/liquidating

The **combination** matters more than either alone. Rising OI with spiking
funding is the classic top signature.
""")

    with st.expander("**ETF flows — the best single predictor**"):
        st.markdown("""
A **Bitcoin ETF** lets traditional investors buy Bitcoin through an ordinary
brokerage account. When they buy, the fund must **actually buy Bitcoin** — real,
mechanical buying pressure.

**Inflows** = money entering = buying. **Outflows** = leaving = selling.

**Why they matter so much:** ETF flows explain roughly **45% of weekly Bitcoin
price moves** — arguably the best predictor available.

**Thresholds:** sustained **>$100M/day inflows** = institutions genuinely
returning. Back below **−$100M/day** = the recovery thesis is dead.
""")

    with st.expander("**Why does crypto follow the Nasdaq?**"):
        st.markdown("""
Because both are **long-duration risk assets**. Tech stocks and crypto are both
bets on future payoffs, so they reprice together when long rates move.

**Use the correlation number on the Terminal page:**
- **Above 0.6** = crypto is trading as a tech proxy → watch the Nasdaq, not
  crypto news
- **Below 0.3** = crypto is running on its own flow → crypto-specific news
  matters more

It recently rose to **0.63** — recent moves were tech-driven, not a decoupling.
""")

# ════════════════════════════════════════════════════ GAUGES
with tabs[6]:
    st.header("🎛️ The gauges and rules")

    a, b = st.columns(2)
    with a:
        st.subheader("DURATION STRESS (0–100)")
        st.markdown("""
**Question:** how hostile are interest rates to crypto right now?

| Range | Meaning | Action |
|---|---|---|
| **0–45** 🟢 | Long rates calm/falling | Rallies stick. Normal size. |
| **45–70** 🟡 | Nothing resolved | Choppy. Smaller size. |
| **70–100** 🔴 | Long end hostile | Fade pops. Minimum size. |

**Built from:** 30Y level (40%) · 30Y 10-day momentum (25%) · bear-steepener
check (20%) · market inflation expectations (15%).

**Why weighted this way:** the level is the actual discount rate, momentum shows
if it's still deteriorating, and the steepener catches the credibility problem a
simple level would miss.
""")
    with b:
        st.subheader("CHOKEPOINT (0–100)")
        st.markdown("""
**Question:** how much war/energy risk is priced in?

| Range | Meaning |
|---|---|
| **0–40** 🟢 | Calm, oil behaving |
| **40–65** 🟡 | Tense, headline-sensitive |
| **65–100** 🔴 | Active disruption priced |

**Built from:** oil momentum + Brent–WTI spread (40%) · tanker stocks (25%) ·
defence stocks (15%) · news volume (20%).

**Why tanker stocks:** when the strait is dangerous, shipping insurance and
freight rates spike — tanker equities front-run that. A tradeable war-risk proxy
that updates faster than news.
""")

    st.divider()
    st.subheader("🚫 THE FADE RULE — the most useful thing here")
    st.markdown("""
**The rule:** if Bitcoin jumps more than 0.8% but the 30Y yield hasn't fallen,
the rally is **not confirmed**. Expect it to reverse.

**Why it works:** crypto is fast, emotional and leveraged. Bonds are slow,
enormous and traded by institutions with no interest in hype. **When crypto
moves and bonds don't agree, the crypto move is just positioning — and
positioning fades.**

**Track record since 29 July: 4 out of 4.** The 30Y ignored oil crashing 25%,
soft inflation data, negative payrolls, and the crypto bill dying. Every pop in
that window faded.

The dashboard checks this automatically and shows a **red banner** when it fires.
""")

    st.divider()
    st.subheader("🎯 Regime labels")
    st.markdown("""
| Regime | Conditions | How to trade |
|---|---|---|
| **RELIEF** 🟢 | Duration low + war premium deflating | Rallies stick. Take directional risk. |
| **TENSE / RANGE** 🟡 | Nothing resolved | Chop. Good for market-making, bad for direction. |
| **DURATION SQUEEZE** 🟠 | Long end hostile | Fade pops. The 4/4 rule is live. |
| **FULL BEAR** 🔴 | Duration hostile + war premium high | Short bias, wide spreads, no grid bots. |
""")

# ════════════════════════════════════════════════════ CHARTS
with tabs[7]:
    st.header("📈 Reading the Terminal charts")

    with st.expander("**Candlesticks — how to read one**", expanded=True):
        st.markdown("""
Each candle covers one period (5 min, 1 hour, 1 day — you choose).

```
      │   ← high (the "wick")
    ┌─┴─┐
    │   │ ← the "body" = open to close
    └─┬─┘
      │   ← low
```

- **Green** = closed higher than it opened (buyers won)
- **Red** = closed lower than it opened (sellers won)
- **Long top wick** = tried to rise, got rejected
- **Long bottom wick** = tried to fall, buyers stepped in
- **Small body** = indecision
- **Big body, no wicks** = strong conviction
""")

    with st.expander("**Moving averages (MA20, MA50)**"):
        st.markdown("""
A **moving average** is the average price over the last N periods, drawn as a
line. It smooths noise so the trend is visible.

- **MA20** (orange) = short-term trend
- **MA50** (blue) = medium-term trend

**How traders use them:**
- Price **above** the MA = uptrend; the MA often acts as **support**
- Price **below** = downtrend; the MA often acts as **resistance**
- MA20 crossing **above** MA50 = bullish signal
- MA20 crossing **below** MA50 = bearish signal

They describe what *has* happened, not what will. Context, not prediction.
""")

    with st.expander("**Support and resistance**"):
        st.markdown("""
- **Support** = a price below where buyers stepped in before. Price often
  bounces. If it **breaks**, expect a faster fall to the next support.
- **Resistance** = a price above where sellers appeared. Price often stalls. A
  convincing break above is bullish.

**The key ones now:**

| Coin | Level | Why |
|---|---|---|
| BTC | **$63,800** | Break = drop toward $61,800 |
| BTC | **$67,300** | Break above = genuine regime change |
| ETH | **$2,000** | Psychological line |
| HYPE | **$52.48** | ⚠️ Most dangerous here — below triggers cascade toward $35 |

**Levels aren't magic.** They tell you *where* a reaction is likely, not *that*
it will happen. Always confirm with the 30Y.
""")

    with st.expander("**The correlation matrix**"):
        st.markdown("""
How closely each pair of assets moved together over 60 days.

- **+1.0** = move perfectly together · **0** = no relationship ·
  **−1.0** = perfectly opposite
- **Green = positive, red = negative**

**What to look for:**
- **BTC↔NDX high (>0.6)** = crypto is a tech proxy right now
- **BTC↔DXY negative** = normal (strong dollar hurts crypto)
- **A correlation that suddenly changes** = the market's driver has changed.
  Often the most valuable signal on the page.
""")

    with st.expander("**Volatility (the 'VOL' metric)**"):
        st.markdown("""
Annualised volatility = how much price swings, as a yearly %.

Rough guide: S&P 500 ~15% · Bitcoin ~50–80% · small altcoin 100%+

**Practical use: it's a position-sizing input.** If BTC's volatility doubles,
the same position size is now twice the risk. Size down — not because you're
more bearish, but because the same bet became bigger.
""")

# ════════════════════════════════════════════════════ ROUTINE
with tabs[8]:
    st.header("☀️ Daily routine")
    st.markdown("""
### The 2-minute morning check (in order)

1. **30Y yield** — up, down, or stuck? *(main page, marked ⭐)*
2. **Duration Stress gauge** — what colour?
3. **Oil / Chokepoint** — any escalation overnight?
4. **Price vs nearest level** — how much room before something happens?
5. **Funding on Hyperliquid** — is everyone crowded one way?

**Decision:**
- 30Y stuck + Duration Stress red → **small size, fade pops, be patient**
- 30Y finally falling → **that's the change you've been waiting for**
""")

    st.divider()
    st.subheader("📋 Trading around a data release")
    st.markdown("""
| When | What to do |
|---|---|
| **Day before** | Find the consensus. Decide scenarios in advance. |
| **1 hour before** | Position or flatten. Don't decide in the moment. |
| **15 min before** | Liquidity already thinning. Widen MM spreads, pause grid bots. |
| **The release** | **Do not trade the first candle.** Watch. |
| **+2–3 min** | Book settled. Now read the real direction. |
| **Confirm** | 30Y → 2Y → DXY → crypto. In that order, always. |
| **After** | Was the reaction consistent with the data? If not, something else is driving. |
""")

    st.divider()
    st.subheader("❌ The seven most common mistakes")
    st.markdown("""
1. **Trading the first candle.** The first 60–90 seconds are noise and often
   reverse. On 29 July the market popped mid-announcement then dropped 1,000
   points.
2. **Assuming bad economic news = good for crypto.** Only true if the 30Y falls.
3. **Adding size into a scheduled event.** Liquidity thins right before releases —
   slippage worsens exactly when you need it not to.
4. **Chasing a move with rising funding.** If funding is spiking, you're the last
   one in.
5. **Trusting a thin prediction market.** $50K volume can be moved by one trader.
   **Volume matters more than the percentage.**
6. **Confusing "expected" with "priced in."** A 70%-expected hold isn't bullish.
7. **Watching only the crypto chart.** Crypto is the shadow; rates and oil are
   the object.
""")

    st.divider()
    st.subheader("🧯 Risk basics")
    st.markdown("""
- **Size for the worst case, not the expected case.** "If this gaps 15% against
  me overnight, am I still fine?"
- **Volatility changes position size.** Same dollar amount ≠ same risk when vol
  doubles.
- **Weekends are dangerous.** Traditional markets close, crypto doesn't. War
  headlines land on Saturdays and gap the Sunday open. Reduce leverage into
  Friday's close.
- **Thin liquidity amplifies everything.** August is seasonally the thinnest
  month.
- **Leverage is for precision, not for size.** If you need leverage to make a
  trade worthwhile, the trade probably isn't worthwhile.
""")

# ════════════════════════════════════════════════════ DICTIONARY
with tabs[9]:
    st.header("📚 Dictionary")
    st.markdown("""
| Term | Plain meaning |
|---|---|
| **AHE** | Average Hourly Earnings — wage growth in the jobs report |
| **Asymmetry** | Upside and downside aren't equal |
| **Basis point (bp)** | 0.01%. "30Y rose 12bp" = rose 0.12% |
| **Bear steepener** | Long yields up, short yields down. Worst case for crypto |
| **Beta** | How much an asset amplifies the market's move |
| **Breakeven** | Market's expected future inflation, derived from bond prices |
| **Cloture** | US Senate procedure to end debate. Needs 60 votes |
| **Consensus** | What economists on average expect. Markets react to the *gap* |
| **Core** | Excluding food and energy |
| **Discount rate** | How much future money is worth today |
| **Dissent** | An FOMC member voting against the decision |
| **Dot plot** | Fed members' anonymous rate forecasts. Quarterly |
| **Dovish** 🕊️ | Leaning toward lower rates. Good for crypto |
| **Duration** | How far in the future an asset's payoff is |
| **DXY** | Dollar strength index. Dollar up = crypto usually down |
| **ETF flows** | Money entering/leaving Bitcoin funds = real buying/selling |
| **FOMC** | The Fed committee that sets rates |
| **Funding rate** | Hourly fee between longs and shorts on perps |
| **GDP deflator** | Broadest inflation measure — the whole economy |
| **Hawkish** 🦅 | Leaning toward higher rates. Bad for crypto |
| **Liquidation** | Forced closure of a leveraged position |
| **Liquidity** | How easily you can trade without moving price. Thin = dangerous |
| **m/m** | Month-over-month change |
| **NFP** | Nonfarm Payrolls — the monthly jobs number |
| **OI** | Open Interest — total money in open positions |
| **Participation rate** | % of adults in the workforce |
| **Passthrough** | How much an input cost (oil) reaches consumer prices |
| **PCE** | The Fed's actual inflation target measure |
| **Perp** | Perpetual future — leveraged bet with no expiry |
| **PMI / ISM** | Business surveys. 50 = expansion/contraction line |
| **Priced in** | Already reflected in the current price |
| **Prices paid** | PMI sub-index = real-time inflation preview |
| **Restrictive** | Policy tight enough to slow the economy |
| **Risk-on / risk-off** | Market appetite for risky assets |
| **SEP** | Summary of Economic Projections — includes the dot plot |
| **Shelter** | Housing costs. ~⅓ of core CPI |
| **Stagflation** | Weak growth + high inflation. The worst case |
| **Supercore** | Core services excluding housing. Fed's persistence gauge |
| **Term premium** | Extra yield demanded for lending long-term |
| **VIX** | Stock market fear gauge |
| **Yield** | The interest rate a bond pays |
| **y/y** | Year-over-year change |
""")

st.divider()
st.caption("Not investment advice. All data delayed. Levels and scenarios are "
           "planning tools, not predictions.")
