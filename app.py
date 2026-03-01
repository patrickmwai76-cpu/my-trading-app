import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Security Credentials
ADMIN_USER = "PATRO_ADMIN"
ADMIN_PASS = "patro666@"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Unlock Terminal"):
        if user == ADMIN_USER and pw == ADMIN_PASS:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Access Denied")

if not st.session_state['logged_in']:
    login()
else:
    # --- TERMINAL LOAD ---
    st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
    st_autorefresh(interval=30000, key="patroupdate")

    # Styling for the "Institutional" look
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #121212; }
        .sop-status { padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-top: 10px; }
        .trend-box { border: 1px solid #4CAF50; color: #4CAF50; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 5px; font-size: 12px; }
        .buy-mode-header { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    # 2. Sidebar - RESTORED LAYOUT
    st.sidebar.title("🛡️ TERMINAL CONTROL")
    
    # Timeframe restored to top of sidebar
    tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    st.sidebar.divider()
    
    # Operator SOP
    st.sidebar.subheader("📋 OPERATOR SOP")
    c1 = st.sidebar.checkbox("Trend Matrix Confluence?")
    c2 = st.sidebar.checkbox("Price Action near VWAP?")
    c3 = st.sidebar.checkbox("News Guard is CLEAR?")
    c4 = st.sidebar.checkbox("Risk Management set?")
    
    if c1 and c2 and c3 and c4:
        st.sidebar.markdown('<div class="sop-status" style="background-color: #006400; color: #90ee90;">✅ READY TO TRADE</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="sop-status" style="background-color: #4b4b00; color: #ffffed;">⚠️ STANDBY</div>', unsafe_allow_html=True)

    st.sidebar.divider()
    
    # Risk Management
    st.sidebar.subheader("📉 RISK MANAGEMENT")
    balance = st.sidebar.number_input("Wallet ($)", value=1000)
    risk_p = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
    lots = (balance * (risk_p/100)) / 50
    st.sidebar.info(f"Suggested Lot Size: {lots:.2f}")

    st.sidebar.divider()
    
    # Trend Matrix
    st.sidebar.subheader("📊 TREND MATRIX")
    st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="trend-box">15M: UP</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
        st.rerun()

    if st.sidebar.button("🔒 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # 3. Main Dashboard
    st.markdown('<div class="buy-mode-header">🛡️ PATRO AI PRO | BUY MODE<br><small>Institutional Scalping Terminal v4.0</small></div>', unsafe_allow_html=True)
    
    st.write("🛡️ **NEWS GUARD ACTIVE**")
    n1, n2 = st.columns(2)
    n1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
    n2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

    # 4. Charting Engine
    df = yf.download("^DJI", period="1d", interval=tf, group_by='column')
    if not df.empty:
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # Indicators & RSI Fix
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))

        # Multi-Layer Chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.15, 0.25])
        
        # Candles & Real Signals
        fig.add_trace(go.Candlestick(x
