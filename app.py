import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. Page Config & Professional Theme
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide", initial_sidebar_state="expanded")

# Auto-refresh every 30 seconds for scalping
st_autorefresh(interval=30000, key="patroupdate")

# Custom Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; }
    .stMetric { background-color: #262626; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 20px; border-radius: 10px; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - OPERATOR SOP & RISK
st.sidebar.title("🛡️ OPERATOR SOP")
sop_1 = st.sidebar.checkbox("Trend Matrix Confluence?")
sop_2 = st.sidebar.checkbox("Price Action near VWAP?")
sop_3 = st.sidebar.checkbox("News Guard is CLEAR?")
sop_4 = st.sidebar.checkbox("Risk Management set?")

if sop_1 and sop_2 and sop_3 and sop_4:
    st.sidebar.success("✅ READY TO TRADE")
else:
    st.sidebar.warning("⚠️ STANDBY")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK CALCULATOR")
balance = st.sidebar.number_input("Balance ($)", value=1000)
risk_p = st.sidebar.slider("Risk (%)", 1.0, 5.0, 1.0)
sl_points = st.sidebar.number_input("SL Points", value=50)
lot_size = (balance * (risk_p/100)) / sl_points
st.sidebar.info(f"Lot Size: {lot_size:.2f}")

# 3. Main Dashboard - Fetching US30 Data
df = yf.download("^DJI", period="1d", interval="1m")

if not df.empty:
    current_price = df['Close'].iloc[-1]
    
    # Header Section
    st.markdown(f'<div class="buy-mode">🛡️ PATRO AI PRO | BUY MODE <br><small>Institutional Scalping Terminal v4.0</small></div>', unsafe_allow_html=True)
    
    # News Guard Area
    col_n1, col_n2 = st.columns(2)
    col_n1.info("📅 Mon Mar 2 | ISM PMI (10:00 AM)")
    col_n2.error("📅 Fri Mar 6 | NFP Jobs (08:30 AM)")

    # Chart Section
    fig = go.Figure()
    # Candlestick Chart
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'))
    # Volume Bars
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2', marker_color='rgba(100,100,100,0.3)'))
    
    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis=dict(title="Price", side="right"),
        yaxis2=dict(title="Volume", overlaying='y', side='left', showgrid=False),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Trend Matrix
    st.subheader("📊 TREND MATRIX")
    st.success("1M: UP")
