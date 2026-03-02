import streamlit as st
import yfinance as yf
import pandas as pd
import time
from lightweight_charts.widgets import StreamlitChart
from streamlit_autorefresh import st_autorefresh

# 1. SECURITY & CONFIG
st.set_page_config(page_title="PATRO AI PRO | LIVE", layout="wide")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR - RESTORED LAYOUT
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("Price Action near VWAP?")
s3 = st.sidebar.checkbox("News Guard is CLEAR?")
s4 = st.sidebar.checkbox("Risk Management set?")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
st.sidebar.info(f"Lot Size: {(bal * 0.01) / 50:.2f}")

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.success("1M: UP | 5M: UP | 15M: UP")

# 3. MAIN INTERFACE
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v4.0</div>', unsafe_allow_html=True)

st.write("🛡️ **NEWS GUARD ACTIVE**")
c1, c2 = st.columns(2)
c1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
c2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

# 4. LIVE STREAMING ENGINE
# This creates the "MT5" moving candle effect
chart = StreamlitChart(width=1100, height=550)

def get_data():
    df = yf.download("YM=F", period="1d", interval=tf, prepost=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    return df

# Initialize Data
data = get_data()
chart.set(data)

# Indicators for the smooth chart
chart.sma(period=20, color='orange')

# Display
chart.load()

# 5. THE LIVE LOOP
# This keeps the price flickering without refreshing the whole page
while True:
    new_tick = yf.download("YM=F", period="1d", interval=tf).tail(1)
    if not new_tick.empty:
        chart.update(new_tick.iloc[0])
    time.sleep(2) # Checks every 2 seconds for a "tick"
