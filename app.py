import streamlit as st
import yfinance as yf
import pandas as pd
import time
from lightweight_charts.widgets import StreamlitChart

# 1. Setup Live Chart (TradingView Style)
st.set_page_config(layout="wide", page_title="PATRO AI PRO | LIVE")

# 2. Sidebar Timeframe Control
st.sidebar.title("🛡️ LIVE TERMINAL")
tf = st.sidebar.selectbox("Select Timeframe", ["1m", "2m", "5m"], index=0)

# 3. Initialize the Chart Object
chart = StreamlitChart(width=1200, height=600)

# 4. Data Logic
def get_live_data():
    # Fetching YM=F (Futures) for real-time motion
    df = yf.download("YM=F", period="1d", interval=tf, prepost=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    return df

# 5. The "Live Loop" (No Autorefresh needed)
# This loop updates the chart every 1 second without reloading the page
data = get_live_data()
chart.set(data) # Load initial historical candles

st.markdown('<div style="background: #00c853; padding: 10px; border-radius: 5px; color: black; text-align: center; font-weight: bold;">🛡️ US30 LIVE STREAMING ACTIVE</div>', unsafe_allow_html=True)

# Display the chart once
chart.load()

# Update the "Current" candle in real-time
while True:
    new_data = yf.download("YM=F", period="1d", interval=tf).tail(1)
    if not new_data.empty:
        # Update the chart with the latest price tick
        chart.update(new_data.iloc[0]) 
    time.sleep(1) # Re-check every second for movement
