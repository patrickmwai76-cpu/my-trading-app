import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config & Professional Theme
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")

# Auto-refresh every 30 seconds to keep the data live
st_autorefresh(interval=30000, key="patroupdate")

# Custom Styling for the "Institutional" look
st.markdown("""
    <style>
    .stMetric { background-color: #262626; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 20px; border-radius: 10px; color: black; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - OPERATOR SOP & RISK
st.sidebar.title("🛡️ OPERATOR SOP")
sop1 = st.sidebar.checkbox("Trend Matrix Confluence?")
sop2 = st.sidebar.checkbox("Price Action near VWAP?")
sop3 = st.sidebar.checkbox("News Guard is CLEAR?")
if sop1 and sop2 and sop3:
    st.sidebar.success("✅ READY TO TRADE")
else:
    st.sidebar.warning("⚠️ STANDBY")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK CALCULATOR")
balance = st.sidebar.number_input("Balance ($)", value=1000)
risk_p = st.sidebar.slider("Risk (%)", 1.0, 5.0, 1.0)
sl_pts = st.sidebar.number_input("SL Points", value=50)
lots = (balance * (risk_p/100)) / sl_pts
st.sidebar.info(f"Suggested Lot: {lots:.2f}")

# 3. Main Dashboard - Fix for the "Alignment Error"
st.markdown('<div class="buy-mode">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL</div>', unsafe_allow_html=True)

# Fetching Data with a fix for the multi-index error
df = yf.download("^DJI", period="1d", interval="1m", group_by='column')

if not df.empty:
    # We grab the 'Close' column specifically to avoid the error
    price = df['Close'].iloc[-1].item()
    avg_p = df['Close'].mean().item()
    hi = df['High'].max().item()
    lo = df['Low'].min().item()
    
    # Trend Matrix Logic
    trend = "UP" if price > avg_p else "DOWN"
    
    # Display Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("US30 Price", f"${price:,.2f}")
    c2.metric("Trend Matrix", f"1M: {trend}")
    c3.metric("Daily Range", f"H: {hi:,.0f} | L: {lo:,.0f}")

    # --- Institutional Chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='US30', line=dict(color='#00ffcc', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=[hi]*len(df), name='Resistance', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=df.index, y=[lo]*len(df), name='Support', line=dict(color='green', dash='dot')))
    
    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0, r=0, t=20, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to fetch market data. Please check your internet connection or GitHub settings.")
