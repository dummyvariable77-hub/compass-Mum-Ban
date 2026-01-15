import streamlit as st
import json
from datetime import datetime, date, time
import math
import pytz

DATA_FILE = "compass_state.json"
IST = pytz.timezone("Asia/Kolkata")
SAVE_TIME = time(9, 15)  # 9:15 AM IST

# ───────── STATE FUNCTIONS ─────────
def load_state():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"position": 50, "last_updated": "1970-01-01"}

def save_state(position):
    with open(DATA_FILE, "w") as f:
        json.dump(
            {
                "position": position,
                "last_updated": str(date.today())
            },
            f
        )

# ───────── TIME LOGIC ─────────
now_ist = datetime.now(IST)
today = str(now_ist.date())
after_915 = now_ist.time() >= SAVE_TIME

state = load_state()
locked_today = state["last_updated"] == today

# ───────── APP ─────────
st.set_page_config(page_title="Mumbai–Bangalore Compass", layout="centered")

st.title("🧭 Mumbai ↔ Bangalore Compass")
st.caption("Daily locked • Adjustable after 9:15 AM IST")

st.markdown(f"**Last adjusted:** {state['last_updated']}")

# ───────── SLIDER (LOCKED LOGIC) ─────────
position = st.slider(
    "Compass Position",
    0,
    100,
    value=int(state["position"]),
    disabled=locked_today,
    help="0 = Mumbai | 50 = Midway | 100 = Bangalore"
)

# ───────── SAVE BUTTON ─────────
if not locked_today:
    if after_915:
        if st.button("Save Today's Position"):
            save_state(position)
            st.success("Saved. Compass locked for today.")
            st.rerun()
    else:
        st.warning("Saving enabled after **9:15 AM IST**.")
else:
    st.info("🔒 Compass locked for today.")

# ───────── BIAS MEANING ─────────
if state["position"] <= 33:
    meaning = "Bias → Mumbai"
elif state["position"] <= 66:
    meaning = "Balanced / Midway"
else:
    meaning = "Bias → Bangalore"

# ───────── COMPASS NEEDLE ─────────
angle_deg = (state["position"] - 50) * 1.8
angle_rad = math.radians(angle_deg)

x = math.cos(angle_rad)
y = math.sin(angle_rad)

st.markdown("### 🧭 Compass")

svg = f"""
<svg width="400" height="200" viewBox="-1.4 -1.2 2.8 2.4">

  <!-- Compass circle -->
  <circle cx="0" cy="0" r="1" stroke="black" stroke-width="0.03" fill="none"/>

  <!-- Horizontal compass line -->
  <line x1="-1" y1="0" x2="1" y2="0" stroke="black" stroke-width="0.03"/>

  <!-- Direction needle -->
  <line x1="0" y1="0" x2="{x}" y2="{-y}" stroke="red" stroke-width="0.05"/>
  <circle cx="0" cy="0" r="0.05" fill="black"/>

  <!-- Labels at ends -->
  <text x="-1.32" y="0.06" font-size="0.2" font-weight="bold" text-anchor="end">
    Mum
  </text>
  <text x="1.32" y="0.06" font-size="0.2" font-weight="bold" text-anchor="start">
    Ban
  </text>

</svg>
"""


st.markdown(svg, unsafe_allow_html=True)
st.metric("Current Compass Bias", meaning)
