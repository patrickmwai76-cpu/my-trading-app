import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="PATRO AI PRO | LIVE", layout="wide")

# 2. FAST REFRESH (10 Seconds for "Live" feel)
st_autorefresh(interval=10000, key="live_pulse")

# 3. Sidebar
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

# 4. Fetch Live Futures (YM=F)
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Live Indicator Update
    df['SMA'] = df['Close'].rolling(20).mean()
    
    # 5. Live Charting
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='Trend'))

    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
    
    st.markdown(f"### 🟢 LIVE DATA STREAMING | Last Tick: {df.index[-1].strftime('%H:%M:%S')}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Waiting for Market Pulse...")
