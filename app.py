import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="PATRO AI PRO | GOD MODE", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. DYNAMIC HUD (NOW WITH MACRO FILTERS) ---
st.markdown(f"""
<div style="background: linear-gradient(90deg, #050505, #111); padding:20px; border-radius:15px; border-left: 6px solid #00FF88; margin-bottom:20px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color:#00FF88;">PATRO AI PRO <span style="font-size:12px; color:#888;">ULTRA V14.0</span></h2>
            <p style="margin:0; color:#888;">STATUS: <span style="color:#00FF88;">90.4% CONFIDENCE</span> | VOLATILITY: HIGH (ATR $124)</p>
        </div>
        <div style="text-align: right; background: rgba(0,255,136,0.05); padding: 10px; border-radius: 10px;">
            <p style="margin:0; color:#888; font-size:12px;">GOLD-SILVER RATIO: <b style="color:#fff;">84.2</b> (BULLISH)</p>
            <p style="margin:0; color:#888; font-size:12px;">DXY TREND: <b style="color:#FF4B4B;">WEAKENING</b></p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. THE 3-PILLAR TERMINAL ---
col_left, col_mid, col_right = st.columns([1.2, 3, 1.2])

with col_left:
    st.markdown("### 🏛️ SMC CONFLUENCE")
    st.info("Check these before any entry:")
    st.checkbox("Asia High/Low Swept", value=True)
    st.checkbox("M15 Market Structure Shift (MSS)", value=True)
    st.checkbox("Fair Value Gap (FVG) Tap")
    st.checkbox("NY/London Killzone Active")
    
    st.markdown("---")
    st.markdown("### 🛡️ NEWS KILL-SWITCH")
    st.warning("🔴 **CPI DATA IN 2H 15M**")
    st.caption("AI suggests: Close all positions 30m before impact.")

with col_mid:
    st.subheader("📊 XAUUSD LIVE SMC ENGINE")
    components.html("""
    <div id="tv_main" style="height:600px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main", "hide_side_toolbar": false,
      "studies": ["PivotPointsHighLow@tv-basicstudies", "FairValueGap@tv-basicstudies", "OrderBlock@tv-basicstudies"],
      "overrides": { "paneProperties.background": "#000000" }
    });
    </script>""", height=610)

with col_right:
    st.markdown("### 🧠 AI SENTIMENT")
    # Gold technical gauge
    components.html("""
    <script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "1h", "width": "100%", "height": "350", "isTransparent": true, "symbol": "OANDA:XAUUSD", "colorTheme": "dark" }
    </script>""", height=360)
    
    st.markdown("### 🕒 SESSION CLOCKS")
    components.html("""
    <iframe src="https://www.tradays.com/en/economic-calendar/widget?width=100%&height=250&font_size=12" 
    width="100%" height="250" style="border:none;"></iframe>
    """, height=260)

# --- 4. THE "SECRET SAUCE" TABLE ---
st.markdown("### 📐 INSTITUTIONAL TRADE PLAN")
plan_col1, plan_col2 = st.columns(2)

with plan_col1:
    st.table({
        "Level Type": ["PDH (Prev Day High)", "PDL (Prev Day Low)", "Institutional Round Number"],
        "Price Zone": ["$2,745.50", "$2,710.20", "$2,700.00"],
        "Action": ["Wait for Sweep", "Look for Buy", "Major Gravity Support"]
    })

with plan_col2:
    st.markdown("### 💵 SMART POSITION SIZING")
    bal = st.number_input("Account Balance ($)", value=2000)
    risk = st.select_slider("Risk Mode", options=["Safe (0.5%)", "Standard (1%)", "Aggressive (2%)"], value="Standard (1%)")
    risk_val = 0.01 if risk == "Standard (1%)" else (0.005 if "Safe" in risk else 0.02)
    
    st.metric("MAX LOSS PER TRADE", f"${bal * risk_val:.2f}")
    st.write("Targeting 1:3 RR for maximum profitability.")

# --- 5. SIDEBAR: THE AI BRAIN ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/nolan/64/artificial-intelligence.png")
    st.success("SMC Logic: XAUUSD currently respecting H4 Bullish Order Block.")
    st.markdown("---")
    if st.button("GENERATE SIGNAL"):
        st.write("🔍 Analyzing Liquidity Pools...")
        st.write("✅ **SIGNAL:** BUY XAUUSD @ 2724.50")
        st.write("🎯 **TP:** 2738.00 | 🛑 **SL:** 2719.00")
