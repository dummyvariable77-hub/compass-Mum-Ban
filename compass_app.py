import streamlit as st
import json
from datetime import datetime, date, time
import math
import pytz
from PIL import Image, ImageDraw, ImageFont
import io

# ───────────────── CONFIG ─────────────────
DATA_FILE = "compass_state.json"
IST = pytz.timezone("Asia/Kolkata")
SAVE_TIME = time(9, 15)

# ───────────────── QUOTES ─────────────────
QUOTES = [
    "Some distances are measured not in miles, but in missing.",
    "Every direction feels empty when the heart knows where it belongs.",
    "Longing is love’s way of pointing home.",
    "Even silence remembers you.",
    "Between here and there, my heart waits.",
    "Distance teaches the heart how deeply it feels.",
    "Every day leans slightly toward where you are.",
    "I miss you in ways the compass cannot measure."
]

def daily_quote():
    return QUOTES[date.today().toordinal() % len(QUOTES)]

# ───────────────── STATE ─────────────────
def load_state():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "position": 50,
            "last_updated": "1970-01-01",
            "ban_count": 0,
            "mum_count": 0
        }

def save_state(position, state):
    if position > 50:
        state["ban_count"] += 1
    elif position < 50:
        state["mum_count"] += 1

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

# Reset to midpoint every new day
if not locked_today:
    state["position"] = 50

# ───────────────── UI ─────────────────
st.set_page_config(page_title="Mumbai–Bangalore Compass", layout="centered")

st.title("🧭 Mumbai ↔ Bangalore Compass")

st.markdown(f"💌 *{daily_quote()}*")
st.markdown(f"**Last adjusted:** {state['last_updated']}")

# ───────────────── SLIDER WITH TEXT LABELS ─────────────────
st.markdown(
    "<div style='display:flex; justify-content:space-between; font-weight:bold;'>"
    "<span>Mumbai</span><span>Bangalore</span></div>",
    unsafe_allow_html=True
)

position = st.slider(
    "",
    0, 100,
    value=int(state["position"]),
    disabled=locked_today,
    help="Left = Mumbai | Mid = Balanced | Right = Bangalore"
)

# ───────────────── SAVE ─────────────────
if not locked_today:
    if after_915:
        if st.button("Save Today's Direction"):
            save_state(position, state)
            st.success("Saved. Direction locked for today.")
            st.rerun()
    else:
        st.warning("Saving enabled after **9:15 AM IST**.")
else:
    st.info("🔒 Direction locked for today.")

# ───────────────── PLAYFUL MESSAGE ─────────────────
if locked_today:
    if state["position"] > 50:
        playful = "💛 Bangalore again. The heart seems certain."
        bias = "Bias → Bangalore"
    elif state["position"] < 50:
        playful = "😅 Mumbai today… the heart hesitated."
        bias = "Bias → Mumbai"
    else:
        playful = "🤍 Midway. Some days don’t choose."
        bias = "Balanced"
else:
    playful = "🤍 Waiting to be decided."
    bias = "Not saved yet"

st.markdown(f"### {playful}")

# ───────────────── COUNTERS ─────────────────
col1, col2 = st.columns(2)
col1.metric("← Mum Days", state["mum_count"])
col2.metric("Ban Days →", state["ban_count"])

# ───────────────── SEMICIRCLE COMPASS ─────────────────
angle_deg = (state["position"] - 50) * 1.8
angle_rad = math.radians(angle_deg)

x = math.cos(angle_rad)
y = math.sin(angle_rad)

st.markdown("### 🧭 Compass")

svg = f"""
<svg width="420" height="240" viewBox="-1.4 -1.1 2.8 1.8">

  <path d="M -1 0 A 1 1 0 0 1 1 0"
        fill="none" stroke="black" stroke-width="0.03"/>

  <line x1="0" y1="0" x2="{x}" y2="{-abs(y)}"
        stroke="red" stroke-width="0.05"/>
  <circle cx="0" cy="0" r="0.05" fill="black"/>

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

# ───────────────── POSTCARD EXPORT ─────────────────
def generate_postcard():
    img = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font = ImageFont.truetype("DejaVuSans.ttf", 22)
    except:
        font_big = font = ImageFont.load_default()

    draw.text((30, 30), "Mumbai ↔ Bangalore", fill="black", font=font_big)
    draw.text((30, 90), f"Date: {today}", fill="black", font=font)
    draw.text((30, 140), f"“{daily_quote()}”", fill="black", font=font)
    draw.text((30, 220), f"Direction: {bias}", fill="black", font=font)
    draw.text((30, 260), playful, fill="black", font=font)
    draw.text((30, 330), f"Mumbai Days: {state['mum_count']}", fill="black", font=font)
    draw.text((30, 360), f"Bangalore Days: {state['ban_count']}", fill="black", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

st.markdown("### 🎴 Daily Postcard")

postcard = generate_postcard()
st.download_button(
    "Download Today's Postcard",
    postcard,
    file_name=f"compass_postcard_{today}.png",
    mime="image/png"
)
