import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup the Page
st.set_page_config(page_title="US30 AI Master Dashboard", layout="wide")

# --- AUTO REFRESH (Every 60 seconds) ---
# This makes the price move on its own!
st_autorefresh(interval=60000, key="us30update")

# 2. Sidebar - All Tools
st.sidebar.title("🚀 US30 AI Control")

# --- Manual Refresh Button ---
if st.sidebar.button("🔄 Force Refresh"):
    st.rerun()

# --- Timeframe Switcher ---
st.sidebar.divider()
st.sidebar.subheader("Select Timeframe")
tf = st.sidebar.radio("Interval", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- Risk & Lot Calculator ---
st.sidebar.divider()
st.sidebar.subheader("Risk Calculator")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_p = st.sidebar.slider("Risk (%)", 1, 5, 1)
sl_points = st.sidebar.number_input("Stop Loss (Points)", value=50)
risk_amt = balance * (risk_p / 100)
lots = risk_amt / sl_points
st.sidebar.info(f"Risk Amount: ${risk_amt:.2f} | Lot Size: {lots:.2f}")

# --- Price Alert ---
st.sidebar.divider()
st.sidebar.subheader("Set Price Alert")
a_price = st.sidebar.number_input("Target Price ($)", value=48000.0)
a_type = st.sidebar.selectbox("Alert When Price Goes:", ["Above", "Below"])

# 3. Main Dashboard Logic
st.title("📈 US30 AI Live Analysis")

# Fetch Market Data
df = yf.download("^DJI", period="1d", interval=tf)

if not df.empty:
    # Get Current Market Stats
    price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].mean().item()
    daily_high = df['High'].max().item()
    daily_low = df['Low'].min().item()
    
    # Top Row Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${price:,.2f}")
    col2.metric("Resistance (High)", f"${daily_high:,.2f}", delta=f"{price-daily_high:,.2f}")
    col3.metric("Support (Low)", f"${daily_low:,.2f}", delta=f"{price-daily_low:,.2f}")

    # --- AI Signal Logic ---
    if price > avg_price:
        st.success(f"🚀 AI SIGNAL: BUY (Bullish) - Target: ${daily_high:,.2f}")
    else:
        st.error(f"📉 AI SIGNAL: SELL (Bearish) - Target: ${daily_low:,.2f}")

    # --- Live Alert Pop-up ---
    if a_type == "Above" and price >= a_price:
        st.toast(f"🚨 ALERT: PRICE REACHED {a_price}!", icon="📈")
        st.warning(f"Target Hit: Price is above {a_price}")
    elif a_type == "Below" and price <= a_price:
        st.toast(f"🚨 ALERT: PRICE REACHED {a_price}!", icon="📉")
        st.warning(f"Target Hit: Price is below {a_price}")

    # --- The Pro Chart ---
    fig = go.Figure()
    # 1. The Main Price Line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Live Price', line=dict(color='#00cfcc', width=3)))
    # 2. The AI Average Baseline
    fig.add_trace(go.Scatter(x=df.index, y=[avg_price]*len(df), name='AI Baseline', line=dict(color='orange', dash='dash')))
    # 3. Resistance (Daily High)
    fig.add_trace(go.Scatter(x=df.index, y=[daily_high]*len(df), name='Resistance (High)', line=dict(color='red', width=1, dash='dot')))
    # 4. Support (Daily Low)
    fig.add_trace(go.Scatter(x=df.index, y=[daily_low]*len(df), name='Support (Low)', line=dict(color='green', width=1, dash='dot')))
    
    # Chart Styling
    fig.update_layout(template="plotly_dark", height=600, margin=dict(l=0, r=0, t=20, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Market data is loading... Please wait 5 seconds.")
