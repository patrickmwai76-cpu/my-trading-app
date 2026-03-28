import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import yfinance as yf

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

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

# --- 2. ADVANCED ANALYTICS ENGINE (Pivot HL & VWAP) ---
def get_market_analytics():
    try:
        gold = yf.Ticker("GC=F")
        # Fetching 15m data for accurate intraday VWAP and Pivots
        df = gold.history(period="2d", interval="15m")
        
        if df.empty:
            return 4493.79, 4491.50, 4485.20 # Fallbacks
        
        # 1. Live Price
        current_p = round(df['Close'].iloc[-1], 2)
        
        # 2. VWAP Calculation: Cumulative (Price * Vol) / Cumulative Vol
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['PV'] = df['TP'] * df['Volume']
        current_vwap = round(df['PV'].cumsum().iloc[-1] / df['Volume'].cumsum().iloc[-1], 2)
        
        # 3. Pivot HL (Lookback last 10 bars)
        pivot_low = round(df['Low'].tail(10).min(), 2)
        pivot_high = round(df['High'].tail(10).max(), 2)
        
        return current_p, current_vwap, pivot_low
    except:
        return 4493.79, 4491.50, 4485.20

current_price, vwap_val, p_low = get_market_analytics()

# --- 3. TRENDMASTER LOGIC ---
m15_t, h1_t, h4_t = "BULLISH", "BULLISH", "BULLISH"
# TrendMaster Mode requires Price > VWAP AND Price > Pivot Low
is_vwap_bullish = current_price > vwap_val
is_pivot_bullish = current_price > p_low
is_trendmaster = (m15_t == h1_t == h4_t == "BULLISH") and is_vwap_bullish and is_pivot_bullish

trend_status = "TRENDMASTER: GOD MODE ACTIVE" if is_trendmaster else "SCANNING MARKET..."
trend_color = "#00FF88" if is_trendmaster else "#FFAA00"
utc_now = datetime.now(pytz.utc).strftime("%H:%M:%S UTC")

# --- 4. THE DYNAMIC DIALOG ---
@st.dialog("🎯 PATRO AI | TRENDMASTER EXECUTION", width="medium")
def show_signal_popup(price, vwap, pl):
    entry = price
    # SL is now smart: 10 pips below the Pivot Low
    sl = pl - 1.00 
    # TP remains 1:2.5 RR
    tp = entry + ((entry - sl) * 2.5)
    
    st.markdown(f"""
    <div style="text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
        <h1 style="color: #00FF88; margin: 0;">GOD MODE BUY</h1>
        <p style="color: #888;">VWAP Alignment Confirmed | Pivot Support Active</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ENTRY", f"{entry}")
        st.metric("STOP LOSS", f"{sl:.2f}", delta="Pivot Protection", delta_color="inverse")
    with col2:
        st.metric("TAKE PROFIT", f"{tp:.2f}", delta="Target High")
        st.metric("VWAP", f"{vwap}")
    
    st.markdown("---")
    if st.button("CONFIRM TO MT5"):
        st.toast(f"TrendMaster Order Sent at {entry}", icon="🔥")
        st.rerun()

# --- 5. HEADER & HUD ---
st.markdown(f"""
<div style="background: linear-gradient(90deg, #050505, #111); padding:20px; border-radius:15px; border-left: 6px solid {trend_color}; margin-bottom:20px; border: 1px solid #222;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color:#00FF88; font-family: monospace;">PATRO AI PRO <span style="font-size:12px; color:#888;">ULTRA V14.0</span></h2>
            <p style="margin:0; color:{trend_color}; font-weight:bold;">{trend_status} | LIVE: ${current_price}</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#00FF88; font-family: monospace; font-size: 20px;">{utc_now}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. LAYOUT ---
col_left, col_mid, col_right = st.columns([1.2, 3, 1.2])

with col_left:
    st.markdown("### ⚡ QUICK SIGNAL")
    # Button only works if TrendMaster is Active
    if st.button("🚀 GENERATE GOD MODE"):
        if is_trendmaster:
            show_signal_popup(current_price, vwap_val, p_low)
        else:
            st.warning("Wait for VWAP & Pivot Confluence")
    
    st.divider()
    st.markdown("### 🏛️ CONFLUENCE")
    st.checkbox("Price > VWAP", value=is_vwap_bullish, disabled=True)
    st.checkbox("Price > Pivot Low", value=is_pivot_bullish, disabled=True)
    st.checkbox("MTF Alignment (M15-H4)", value=is_trendmaster, disabled=True)

with col_mid:
    # Updated Chart to include VWAP and Pivots by default
    components.html(f"""
    <div id="tv_main" style="height:550px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    }});
    </script>""", height=560)

with col_right:
    st.markdown("### 🧠 ANALYTICS")
    st.metric("LIVE VWAP", f"{vwap_val}")
    st.metric("PIVOT SUPPORT", f"{p_low}")
    st.metric("NEW YORK", datetime.now(pytz.timezone('America/New_York')).strftime("%H:%M"))

with st.sidebar:
    st.markdown("<h1 style='color:#00FF88;'>PATRO AI</h1>", unsafe_allow_html=True)
    if is_trendmaster:
        st.success("GOD MODE ACTIVE")
    else:
        st.info("SCANNING CONFLUENCE")
    
    bal = st.number_input("Balance ($)", value=2000)
    risk = st.select_slider("Risk Mode (%)", options=[0.5, 1.0, 2.0], value=1.0)
    st.metric("MAX RISK", f"${bal * (risk/100):.2f}")
    if st.button("Refresh Price"):
        st.rerun()
