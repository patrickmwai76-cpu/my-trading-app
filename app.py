import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.0", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None

# 2. SECURITY
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. SIDEBAR: INSTITUTIONAL SOP & CONTROLS
with st.sidebar:
    st.title("🎮 PATRO CONTROL")
    st.divider()
    
    st.subheader("📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    st.subheader("⚙️ SETTINGS")
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    if st.button("♻️ RESET SIGNAL LOCK", use_container_width=True):
        st.session_state.trade_lock = None
        st.rerun()

# 4. DATA ENGINE
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df
