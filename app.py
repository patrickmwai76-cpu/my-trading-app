import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config & Professional Theme
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Custom Dark Theme CSS
st.markdown("""
    <style>
    .stMetric { background-color: #262626; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    .trend-box { padding: 10px; border-radius: 5px; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold; margin-bottom: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - TERMINAL CONTROL
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MANAGEMENT")
wallet = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
lots = (wallet * (risk_p/100)) / 50
st.sidebar.info(f"Suggested Lot Size: {lots:.2f}")

# Trend Matrix Logic (Simulated for UI)
st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">15M: UP</div>', unsafe_allow_html=True)

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Main Dashboard Data
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    # Fix for multi-index error
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Technical Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    # Basic RSI calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1, + rs))

    # Subplots: Price on top (row 1), RSI on bottom (row 2)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # Price Chart & Buy/Sell Logic
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend Line', line=dict(color='orange', width=1)), row=1, col=1)

    # RSI (Purple Line at bottom)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Unavailable")
