import streamlit as st
import json
from datetime import datetime, date, time
import math
import pytz

# ───────────────── CONFIG ─────────────────
DATA_FILE = "compass_state.json"
IST = pytz.timezone("Asia/Kolkata")
SAVE_TIME = time(9, 15)  # 9:15 AM IST

# ───────────────── ROMANTIC QUOTES ─────────────────
QUOTES = [
    "Some distances are measured not in miles, but in missing.",
    "Every direction feels empty when the heart knows where it belongs.",
    "Longing is love’s way of pointing home.",
    "Even silence remembers you.",
    "I miss you in ways the compass cannot measure.",
    "Between here and there, my heart waits.",
    "Distance teaches the heart how deeply it feels.",
    "Every day leans slightly toward where you are."
]

def daily_quote():
    return QUOTES[date.today().toordinal() % len(QUOTES)]

# ───────────────── STATE FUNCTIONS ─────────────────
def load_state():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "position": 50,
            "last_updated": "1970-01-01",
            "ban_count": 0,
            "mum_count": 0,
            "ban_streak": 0,
            "last_month": ""
        }

def save_state(position, state):
    if position > 50:
        state["ban_count"] += 1
        state["ban_streak"] += 1
    elif position < 50:
        state["mum_count"] += 1
        state["ban_streak"] = 0
    else:
        state["ban_streak"] = 0

    state["position"] = position
    state["last_updated"] = str(date.today())

    with open(DATA_FILE, "w") as f:
        json.dump(state, f)

# ───────────────── TIME LOGIC ─────────────────
now_ist = datetime.now(IST)
today = str(now_ist.date())
after_915 = now_ist.time() >= SAVE_TIME

state = load_state()
locked_today = state["last_updated"] == today

# Reset compass daily
if not locked_today:
    state["position"] = 50

# ───────────────── APP UI ─────────────────
st.set_page_config(page_title="Mumbai–Bangalore Compass", layout="centered")

# Teddy image
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/0/0b/Teddy_bear_2003.jpg",
    width=90
)

st.title("🧭 Mumbai ↔ Bangalore Compass")


# Quote
st.markdown(f"💌 *{daily_quote()}*")

# Monthly summary
current_month = date.today().strftime("%Y-%m")
if state["last_month"] != current_month:
    if state["ban_count"] > state["mum_count"]:
        st.info("❤️ Last month, the heart leaned more toward Bangalore.")
    elif state["ban_count"] < state["mum_count"]:
        st.info("💭 Last month wandered more toward Mumbai.")
    else:
        st.info("🤍 Last month stayed beautifully balanced.")
    state["last_month"] = current_month
    with open(DATA_FILE, "w") as f:
        json.dump(state, f)

st.markdown(f"**Last adjusted:** {state['last_updated']}")

# ───────────────── SLIDER ─────────────────
position = st.slider(
    "Compass Position",
    0,
    100,
    value=int(state["position"]),
    disabled=locked_today,
    help="Left = Mumbai | Mid = Balance | Right = Bangalore"
)

# ───────────────── SAVE LOGIC ─────────────────
if not locked_today:
    if after_915:
        if st.button("Save Today's Direction"):
            save_state(position, state)
            st.success("Saved. Direction remembered for today.")
            st.rerun()
    else:
        st.warning("Saving opens after **9:15 AM IST**.")
else:
    st.info("🔒 Direction locked for today.")

# ───────────────── PLAYFUL MESSAGE ─────────────────
if locked_today:
    if state["position"] > 50:
        if state["ban_streak"] >= 3:
            playful = "🐻🏆 Bangalore again! Teddy is proud — this is becoming a habit."
        else:
            playful = "🐻💛 Teddy smiles. Bangalore feels right today."
    elif state["position"] < 50:
        playful = "🐻😅 Mumbai today… Teddy raises an eyebrow, but stays kind."
    else:
        playful = "🐻🤍 Teddy waits quietly. Some days don’t need choosing."
else:
    if position > 50:
        playful = "🐻✨ Ooo… drifting toward Bangalore already!"
    elif position < 50:
        playful = "🐻🙃 Teddy gently nudges right. Just saying."
    else:
        playful = "🐻🫶 Midway. No pressure."

st.markdown(f"### {playful}")

# ───────────────── COUNTERS ─────────────────
col1, col2 = st.columns(2)

col1.markdown(
    f"<div style='opacity:0.6'>← Mum Days<br><b>{state['mum_count']}</b></div>",
    unsafe_allow_html=True
)

col2.metric("Ban Days →", state["ban_count"])

# ───────────────── SEMICIRCLE COMPASS ─────────────────
angle_deg = (state["position"] - 50) * 1.8
angle_rad = math.radians(angle_deg)

x = math.cos(angle_rad)
y = math.sin(angle_rad)

st.markdown("### 🧭 Compass")

svg = f"""
<svg width="420" height="240" viewBox="-1.4 -1.1 2.8 1.8">

  <!-- Semicircle arc -->
  <path d="M -1 0 A 1 1 0 0 1 1 0"
        fill="none" stroke="black" stroke-width="0.03"/>

  <!-- Needle -->
  <line x1="0" y1="0" x2="{x}" y2="{-abs(y)}"
        stroke="red" stroke-width="0.05"/>
  <circle cx="0" cy="0" r="0.05" fill="black"/>

  <!-- Labels -->
  <rect x="-1.48" y="-0.12" width="0.48" height="0.24" fill="white"/>
  <text x="-1.24" y="0.08" font-size="0.2" font-weight="bold"
        text-anchor="middle">Mum</text>

  <rect x="-0.24" y="-0.55" width="0.48" height="0.22" fill="white"/>
  <text x="0" y="-0.38" font-size="0.16" font-weight="bold"
        text-anchor="middle">Mid</text>

  <rect x="1.00" y="-0.12" width="0.48" height="0.24" fill="white"/>
  <text x="1.24" y="0.08" font-size="0.2" font-weight="bold"
        text-anchor="middle">Ban</text>

</svg>
"""

st.markdown(svg, unsafe_allow_html=True)
