import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="US30 AI Pro Dashboard", layout="wide")

# 2. Sidebar - All Trading Tools
st.sidebar.title("🛠️ US30 Control Panel")

# --- Manual Refresh (The only way to update now) ---
if st.sidebar.button("🔄 Update Market Price"):
    st.rerun()

# --- Timeframe Switcher ---
st.sidebar.divider()
st.sidebar.subheader("Select Timeframe")
tf = st.sidebar.radio("Interval", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- Risk & Lot Calculator ---
st.sidebar.divider()
st.sidebar.subheader("Risk & Lot Calculator")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_p = st.sidebar.slider("Risk (%)", 1, 5, 1)
sl_points = st.sidebar.number_input("Stop Loss (Points)", value=50)

risk_amt = balance * (risk_p / 100)
lots = risk_amt / sl_points
st.sidebar.info(f"Risk: ${risk_amt:.2f} | Lot Size: {lots:.2f}")

# --- Price Alert ---
st.sidebar.divider()
st.sidebar.subheader("Set Price Alert")
a_price = st.sidebar.number_input("Alert Price ($)", value=48000.0)
a_type = st.sidebar.selectbox("Alert When Price Goes:", ["Above", "Below"])

# 3. Main Dashboard Logic
st.title("📊 US30 AI Live Analysis")

# Fetch Data (Yahoo Finance)
df = yf.download("^DJI", period="1d", interval=tf)

if not df.empty:
    price = df['Close'].iloc[-1].item()
    avg_price = df['Close'].mean().item()
    daily_high = df['High'].max().item()
    daily_low = df['Low'].min().item()
    
    # --- Top Metrics ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Price", f"${price:,.2f}")
    m2.metric("Resistance (High)", f"${daily_high:,.2f}")
    m3.metric("Support (Low)", f"${daily_low:,.2f}")

    # --- AI Signal ---
    if price > avg_price:
        st.success(f"🚀 AI SIGNAL: BUY (Targeting High: {daily_high:,.2f})")
    else:
        st.error(f"📉 AI SIGNAL: SELL (Targeting Low: {daily_low:,.2f})")

    # --- Alerts ---
    if a_type == "Above" and price >= a_price:
        st.toast(f"🚨 ALERT: PRICE ABOVE {a_price}!", icon="📈")
        st.warning(f"Target Hit: ${price:,.2f} is above your {a_price} alert!")
    elif a_type == "Below" and price <= a_price:
        st.toast(f"🚨 ALERT: PRICE BELOW {a_price}!", icon="📉")
        st.warning(f"Target Hit: ${price:,.2f} is below your {a_price} alert!")

    # --- Pro Interactive Chart ---
    fig = go.Figure()
    
    # Live Price Line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#00cfcc', width=2)))
    
    # AI Average Baseline
    fig.add_trace(go.Scatter(x=df.index, y=[avg_price]*len(df), name='AI Baseline', line=dict(color='orange', dash='dash')))
    
    # Resistance Line (Red)
    fig.add_trace(go.Scatter(x=df.index, y=[daily_high]*len(df), name='Daily High', line=dict(color='red', width=1, dash='dot')))
    
    # Support Line (Green)
    fig.add_trace(go.Scatter(x=df.index, y=[daily_low]*len(df), name='Daily Low', line=dict(color='green', width=1, dash='dot')))
    
    # Chart Styling
    fig.update_layout(
        template="plotly_dark", 
        height=600, 
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Market is closed or loading data... please wait.")
