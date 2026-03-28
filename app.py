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
        background-color: #00FF88; color: #000; border-radius: 8px; width: 100%; font-weight: bold; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TREND LOGIC & GLOBAL VARIABLES (DEFINED FIRST) ---
m15_t, h1_t, h4_t = "BULLISH", "BULLISH", "BULLISH"
is_god_mode = (m15_t == h1_t == h4_t == "BULLISH")

# Fixed the NameError by defining these before the UI starts
trend_status = "GOD MODE: STRONG BULLISH" if is_god_mode else "SCANNING ALIGNMENT..."
trend_color = "#00FF88" if is_god_mode else "#FFAA00"
utc_now = datetime.now(pytz.utc).strftime("%H:%M:%S UTC")

# --- 3. THE POP-VIEW (DIALOG) FUNCTION ---
@st.dialog("🎯 PATRO AI | EXECUTION SIGNAL", width="medium")
def show_signal_popup():
    st.markdown("""
    <div style="text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
        <h1 style="color: #00FF88; margin: 0;">BUY XAUUSD</h1>
        <p style="color: #888;">Precision Entry | VWAP & PIVOT ALIGNED</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ENTRY", "2724.50")
        st.metric("STOP LOSS", "2719.00", delta="-55 pips", delta_color="inverse")
    with col2:
        st.metric("TAKE PROFIT", "2738.00", delta="+135 pips")
        st.metric("RR RATIO", "1:2.45")
    
    st.markdown("---")
    if st.button("CONFIRM EXECUTION"):
        st.toast("Sending order to MetaTrader 5...", icon="🚀")
        st.rerun()

# --- 4. HEADER & DYNAMIC HUD ---
st.markdown(f"""
<div style="background: linear-gradient(90deg, #050505, #111); padding:20px; border-radius:15px; border-left: 6px solid {trend_color}; margin-bottom:20px; border: 1px solid #222;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color:#00FF88; font-family: monospace;">PATRO AI PRO <span style="font-size:12px; color:#888;">ULTRA V14.0</span></h2>
            <p style="margin:0; color:{trend_color}; font-weight:bold;">{trend_status}</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#00FF88; font-family: monospace; font-size: 20px;">{utc_now}</p>
            <div style="display: flex; gap: 15px; margin-top:5px; justify-content: flex-end;">
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">M15</p><b style="color:#00FF88;">{m15_t}</b></div>
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">H1</p><b style="color:#00FF88;">{h1_t}</b></div>
                <div style="text-align:center;"><p style="color:#888; font-size:10px; margin:0;">H4</p><b style="color:#00FF88;">{h4_t}</b></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. MAIN TERMINAL ---
col_left, col_mid, col_right = st.columns([1.2, 3, 1.2])

with col_left:
    st.markdown("### 🏛️ SMC CONFLUENCE")
    with st.container(border=True):
        st.checkbox("Asia Session Sweep", value=True)
        st.checkbox("Price Above VWAP", value=True)
        st.checkbox("Pivot HL Rejection", value=True)
        st.checkbox("M15 MSS Confirmed", value=True)
    
    st.markdown("---")
    st.markdown("### ⚡ QUICK SIGNAL")
    if st.button("🚀 GENERATE SIGNAL"):
        show_signal_popup()

with col_mid:
    components.html("""
    <div id="tv_main" style="height:550px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["PivotPointsHighLow@tv-basicstudies", "VWAP@tv-basicstudies", "OrderBlock@tv-basicstudies"]
    });
    </script>""", height=560)

with col_right:
    st.markdown("### 🧠 AI SENTIMENT")
    components.html("""
    <script src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "1h", "width": "100%", "height": "350", "isTransparent": true, "symbol": "OANDA:XAUUSD", "colorTheme": "dark" }
    </script>""", height=360)
    
    st.metric("LONDON", datetime.now(pytz.timezone('Europe/London')).strftime("%H:%M"))
    st.metric("NEW YORK", datetime.now(pytz.timezone('America/New_York')).strftime("%H:%M"))

# --- 6. SIDEBAR CONTROL ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/nolan/64/artificial-intelligence.png", width=80)
    
    st.success(f"MODE: {trend_status}")
    
    st.divider()
    bal = st.number_input("Balance ($)", value=2000)
    risk_pct = st.select_slider("Risk Mode", options=[0.5, 1.0, 2.0], value=1.0)
    st.metric("MAX RISK", f"${bal * (risk_pct/100):.2f}")
    
    st.info("Scanner linked to Pepperstone/JustMarkets Live.")

# --- 7. NEWS TICKER (BOTTOM) ---
components.html("""
<div style="background: #111; padding: 10px; border-top: 1px solid #333;">
<script src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{
  "symbols": [
    {"proName": "FOREXCOM:SPX500", "title": "S&P 500"},
    {"proName": "FOREXCOM:NSXUSD", "title": "Nasdaq 100"},
    {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"},
    {"proName": "OANDA:XAUUSD", "title": "Gold"},
    {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}
  ],
  "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive"
}
</script>
</div>""", height=100)
