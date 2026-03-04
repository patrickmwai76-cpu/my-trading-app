import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. SETUP
st.set_page_config(page_title="PATRO AI PRO V9.0", layout="wide")

# 2. SIDEBAR (COMPACT)
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_macd = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    st.markdown("### ⚙️ VISUALS")
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    current_tf = st.radio("Display Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)

# 3. MULTI-TIMEFRAME DATA ENGINE
@st.cache_data(ttl=30)
def get_trend_status(ticker, tf_list):
    status = {}
    for tf in tf_list:
        df = yf.download(ticker, period="1d", interval=tf, progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Calculate Trend
        macd = ta.macd(df['Close'])
        vwap = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        
        last_close = df['Close'].iloc[-1]
        last_macd = macd.iloc[-1, 1] # Histogram
        
        if last_close > vwap.iloc[-1] and last_macd > 0:
            status[tf] = "BUY"
        elif last_close < vwap.iloc[-1] and last_macd < 0:
            status[tf] = "SELL"
        else:
            status[tf] = "NEUTRAL"
    return status

# 4. TREND ALIGNMENT BOX (THE BOX YOU ASKED FOR)
trends = get_trend_status(asset_map[asset_label], ["1m", "5m", "15m"])

st.markdown("### 🛰️ MULTI-TIMEFRAME ALIGNMENT")
cols = st.columns(4)
cols[0].metric("1m Trend", trends["1m"])
cols[1].metric("5m Trend", trends["5m"])
cols[2].metric("15m Trend", trends["15m"])

# THE MASTER SIGNAL BOX
with cols[3]:
    if trends["1m"] == trends["5m"] == trends["15m"] == "BUY":
        st.success("🔥 CONFLUENCE: ALL-TIME BUY")
    elif trends["1m"] == trends["5m"] == trends["15m"] == "SELL":
        st.error("❄️ CONFLUENCE: ALL-TIME SELL")
    else:
        st.warning("⚠️ WAITING FOR ALIGNMENT")

# 5. MAIN CHART ENGINE
# [Rest of the charting code from V8.9 remains here for Volume and MACD Rows]
