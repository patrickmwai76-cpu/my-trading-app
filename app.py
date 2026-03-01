import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(page_title="US30 AI Pro", layout="wide")

# --- AUTO REFRESH (Every 60 seconds) ---
# This keeps the price moving even if you don't touch the phone
st_autorefresh(interval=60000, key="us30update")

# 2. Sidebar - Trading Tools
st.sidebar.title("🛠️ Trading Tools")

# --- Manual Refresh Button ---
if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# --- Timeframe Switcher ---
st.sidebar.divider()
st.sidebar.subheader("Select Timeframe")
timeframe = st.sidebar.radio("Interval", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- Risk Calculator ---
st.sidebar.divider()
st.sidebar.subheader("Risk Calculator")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_percent = st.sidebar.slider("Risk (%)", 1, 5, 1)
stop_loss_pips = st.sidebar.number_input("Stop Loss (Points)", value=50)

risk_amount = balance * (risk_percent / 100)
lot_size = risk_amount / stop_loss_pips
st.sidebar.info(f"Risk Amount: ${risk_amount:.2f}\n\nSuggested Lot: {lot_size:.2f}")

# --- Price Alert Setup ---
st.sidebar.divider()
st.sidebar.subheader("Set Price Alert")
alert_price = st.sidebar.number_input("Alert Price ($)", value=48000.0)
alert_type = st.sidebar.selectbox("Alert When Price Goes:", ["Above", "Below"])

# 3. Main Dashboard - Data Fetching
st.title("📊 US30 AI Live Dashboard")

# Fetching data based on your timeframe selection
df = yf.download("^DJI", period="1d", interval=timeframe)

if not df.empty:
    price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].mean().item()
    
    # Metrics display
    col1, col2 = st.columns(2)
    col1.metric("Current US30", f"${price:,.2f}")
    col2.metric("Daily Average", f"${avg_price:,.2f}")

    # --- AI Signal Logic ---
    if price > avg_price:
        st.success("🚀 AI SIGNAL: BUY (Bullish Momentum)")
    else:
        st.error("📉 AI SIGNAL: SELL (Bearish Trend)")

    # --- Price Alert Logic ---
    if alert_type == "Above" and price >= alert_price:
        st.toast(f"🚨 ALERT: US30 is ABOVE {alert_price}!", icon="📈")
    elif alert_type == "Below" and price <= alert_price:
        st.toast(f"🚨 ALERT: US30 is BELOW {alert_price}!", icon="📉")

    # --- Professional Interactive Chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00cfcc', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=[avg_price]*len(df), name='AI Baseline', line=dict(color='orange', dash='dash')))
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Fetching Market Data... Markets may be closed or loading.")
