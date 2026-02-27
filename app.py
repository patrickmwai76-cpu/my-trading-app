import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pandas_ta as ta
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="US30 AI Pro", layout="wide")

# --- CUSTOM CSS FOR "PRO" LOOK ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: RISK CALCULATOR ---
with st.sidebar:
    st.header("🛠️ Trading Tools")
    st.subheader("Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 1, 5, 1)
    stop_loss = st.number_input("Stop Loss (Points)", value=50)
    
    risk_amt = balance * (risk_pct / 100)
    lot_size = risk_amt / stop_loss if stop_loss > 0 else 0
    
    st.write(f"Risk Amount: **${risk_amt:.2f}**")
    st.write(f"Suggested Lot: **{lot_size:.2f}**")

# --- MAIN DASHBOARD ---
st.title("📊 US30 AI Live Dashboard")

# Top Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Current US30", "$48,914.18", "+1.2%")
col2.metric("Daily Average", "$48,852.94")
col3.metric("AI Confidence", "87%", "Strong")

# --- GENERATE PRO CHART DATA ---
# This creates dummy data that looks like a real market
dates = [datetime.now() - timedelta(minutes=i) for i in range(100)]
data = {
    'Date': dates[::-1],
    'Open': np.random.uniform(48800, 48900, 100),
    'High': np.random.uniform(48900, 48950, 100),
    'Low': np.random.uniform(48750, 48800, 100),
    'Close': np.random.uniform(48800, 48900, 100)
}
df = pd.DataFrame(data)

# Add a Technical Indicator (SMA 20)
df['SMA20'] = ta.sma(df['Close'], length=20)

# --- CANDLESTICK CHART ---
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], 
    low=df['Low'], close=df['Close'], name='US30'
))
fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA20'], line=dict(color='orange', width=1.5), name='SMA 20'))

fig.update_layout(
    template='plotly_dark',
    height=450,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_rangeslider_visible=False
)
st.plotly_chart(fig, use_container_width=True)

# --- ALERTS & SIGNALS ---
st.info("🚀 AI SIGNAL: BUY (Strong Momentum)")

if st.button("Simulate Price Target"):
    st.success("PRICE TARGET REACHED: $48,914.18")
    st.toast('Target Hit!', icon='🎯')
    st.balloons()
