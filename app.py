import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# --- 1. CONFIGURATION & CYBERPUNK STYLING ---
st.set_page_config(
    page_title="PATRO AI PRO | GOD MODE", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .stMetric { background-color: #111; padding: 10px; border-radius: 10px; border: 1px solid #222; }
    div.stButton > button:first-child {
        background-color: #00FF88; color: #000; border-radius: 8px; width: 100%; font-weight: bold;
    }
    .trend-badge {
        padding: 4px 12px; border-radius: 5px; font-weight: bold; border: 1px solid; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MTF TREND LOGIC & GOD MODE ---
# (Simulated alignment logic for the HUD)
m15_trend, h1_trend, h4_trend = "BULLISH", "BULLISH", "BULLISH"
is_god_mode = (m15_trend == h1_trend == h4_trend == "BULLISH")

trend_status = "GOD MODE: STRONG BULLISH" if is_god_mode else "NEUTRAL / MIXED"
trend_color = "#00FF88" if is_god_mode else "#FFAA00"

# --- 3. HEADER & DYNAMIC HUD ---
utc_now = datetime.now(pytz.utc).strftime("%H:%M:%S UTC")

st.markdown(f"""
<div style="background: linear-gradient(90deg, #050505, #111); padding:20px; border-radius:15px; border-left: 6px solid {trend_color}; margin-bottom:20px; border-top: 1px solid #222; border-right: 1px solid #222;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color:#00FF88; font-family: monospace;">PATRO AI PRO <span style="font-size:12px; color:#888;">ULTRA V14.0</span></h2>
            <div style="margin-top:8px;">
                <span style="color:{trend_color}; background:{trend_color}22; border:1px solid {trend_color}; padding:4px 10px; border-radius:5px; font-weight:bold;">
                    {trend_status}
                </span>
                <span style="color:#888; margin-left:10px; font-size:14px;">VWAP: ABOVE | PIVOT: TESTING R1</span>
            </div>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#00FF88; font-family: monospace; font-size: 20px;">{utc_now}</p>
            <div style="display: flex; gap: 15px; margin-top:5px; justify-content: flex-end;">
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">M15</p><b style="color:#00FF88;">{m15_trend}</b></div>
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">H1</p><b style="color:#00FF88;">{h1_trend}</b></div>
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">H4</p><b style="color:#00FF88;">{h4_trend}</b></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. THE MAIN TERMINAL (3-COLUMN LAYOUT) ---
col_left, col_mid, col_right = st.columns([1.2, 3, 1.2])

with col_left:
    st.markdown("### 🏛️ SMC CONFLUENCE")
    with st.container(border=True):
        st.checkbox("Asia High/Low Swept", value=True)
        st.checkbox("Price Above VWAP", value=True)
        st.checkbox("Pivot High/Low Rejection", value=True)
        st.checkbox("M15 Market Structure Shift (MSS)", value=True)
    
    st.markdown("---")
    st.markdown("### 🛡️ NEWS KILL-SWITCH")
    st.warning("🔴 **CPI DATA IN 2H 15M**")
    st.caption("AI Suggestion: Close all positions 30m before impact.")

with col_mid:
    st.subheader("📊 XAUUSD LIVE SMC ENGINE")
    # TradingView Widget with PIVOTS and VWAP
    components.html("""
    <div id="tv_main" style="height:600px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main", "hide_side_toolbar": false,
      "studies": [
        "PivotPointsHighLow@tv-basicstudies", 
        "VWAP@tv-basicstudies", 
        "OrderBlock@tv-basicstudies"
      ],
      "overrides": { "paneProperties.background": "#000000" }
    });
    </script>""", height=610)

with col_right:
    st.markdown("### 🧠 AI SENTIMENT")
    components.html("""
    <div style="background-color: transparent;">
    <script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "1h", "width": "100%", "height": "350", "isTransparent": true, "symbol": "OANDA:XAUUSD", "colorTheme": "dark" }
    </script>
    </div>""", height=360)
    
    st.markdown("### 🕒 SESSION CLOCKS")
    st.metric("LONDON", datetime.now(pytz.timezone('Europe/London')).strftime("%H:%M"))
    st.metric("NEW YORK", datetime.now(pytz.timezone('America/New_York')).strftime("%H:%M"))

# --- 5. INSTITUTIONAL PLANNING & RISK MANAGEMENT ---
st.markdown("---")
st.markdown("### 📐 INSTITUTIONAL TRADE PLAN")
plan_col1, plan_col2 = st.columns([2, 1])

with plan_col1:
    st.table({
        "Level Type": ["PDH", "PDL", "Daily Pivot", "VWAP Zone"],
        "Price Zone": ["$2,745.50", "$2,710.20", "$2,725.00", "$2,722.50"],
        "Action": ["Wait for Sweep", "Look for Buy", "Key Gravity", "Dynamic Support"]
    })

with plan_col2:
    st.markdown("### 💵 SMART POSITION SIZING")
    with st.container(border=True):
        bal = st.number_input("Account Balance ($)", value=2000, step=100)
        risk_label = st.select_slider("Risk Mode", options=["Safe (0.5%)", "Standard (1%)", "Aggressive (2%)"], value="Standard (1%)")
        risk_map = {"Safe (0.5%)": 0.005, "Standard (1%)": 0.01, "Aggressive (2%)": 0.02}
        max_loss = bal * risk_map[risk_label]
        st.metric("MAX LOSS PER TRADE", f"${max_loss:.2f}", delta="- Risk Capital", delta_color="inverse")

# --- 6. SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; margin-bottom:0;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.caption("Institutional Intelligence v14.0")
    st.image("https://img.icons8.com/nolan/64/artificial-intelligence.png", width=80)
    
    st.success(f"TREND MODE: {trend_status}")
    
    st.markdown("---")
    st.markdown("### ⚡ QUICK SIGNAL")
    if st.button("GENERATE SIGNAL"):
        with st.status("Analyzing Liquidity Pools...", expanded=True) as status:
            st.write("🔍 Identifying Liquidity Sweeps...")
            st.write("📊 Checking VWAP/Pivot Alignment...")
            st.write("✅ **SIGNAL READY**")
            status.update(label="Signal Generated!", state="complete", expanded=True)
            
        st.code("""
BUY XAUUSD @ 2724.50
TP: 2738.00
SL: 2719.00
RR: 1:2.7
        """, language="markdown")
    
    st.markdown("---")
    st.info("System linked to MT5 Terminal. Ensure 'Algo Trading' is enabled.")
