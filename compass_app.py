import streamlit as st
import json
from datetime import date
import math

DATA_FILE = "compass_state.json"

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

# ───────── APP ─────────
st.set_page_config(page_title="Mumbai–Bangalore Compass", layout="centered")

st.title("🧭 Mumbai ↔ Bangalore Compass")
st.caption("Daily locked • Persistent • Shared")

state = load_state()
today = str(date.today())

st.markdown(f"**Last adjusted:** {state['last_updated']}")

# ───────── SLIDER (BOUND TO SAVED VALUE) ─────────
position = st.slider(
    "Compass Position",
    0,
    100,
    value=int(state["position"]),
    help="0 = Bangalore | 50 = Midway | 100 = Mumbai"
)

# ───────── SAVE LOGIC ─────────
if today != state["last_updated"]:
    if st.button("Save Today's Position"):
        save_state(position)
        st.success("Saved. Compass locked for today.")
        st.rerun()
else:
    st.info("Compass is locked for today. You can adjust again tomorrow.")

# ───────── MEANING ─────────
if state["position"] <= 33:
    meaning = "Bias → Bangalore"
elif state["position"] <= 66:
    meaning = "Balanced / Midway"
else:
    meaning = "Bias → Mumbai"

# ───────── COMPASS NEEDLE ─────────
angle_deg = (state["position"] - 50) * 1.8
angle_rad = math.radians(angle_deg)

x = math.cos(angle_rad)
y = math.sin(angle_rad)

st.markdown("### 🧭 Compass")

svg = f"""
<svg width="300" height="300" viewBox="-1.2 -1.2 2.4 2.4">
  <circle cx="0" cy="0" r="1" stroke="black" stroke-width="0.03" fill="none"/>
  <line x1="0" y1="0" x2="{x}" y2="{-y}" stroke="red" stroke-width="0.05"/>
  <circle cx="0" cy="0" r="0.05" fill="black"/>
  <text x="-1" y="0" font-size="0.15" text-anchor="start">Bangalore</text>
  <text x="1" y="0" font-size="0.15" text-anchor="end">Mumbai</text>
</svg>
"""

st.markdown(svg, unsafe_allow_html=True)

st.metric("Current Compass Bias", meaning)
