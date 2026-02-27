import streamlit as st

# --- ERROR CHECKER ---
try:
    import pandas as pd
    import numpy as np
    import pandas_ta as ta
    import plotly.graph_objects as go
    import yfinance as yf
except ImportError as e:
    st.error(f"Missing Library: {e}")
    st.stop()

st.set_page_config(page_title="US30 AI Pro", layout="wide")

# Sidebar Logic
with st.sidebar:
    st.header("🛠️ Risk Setup")
    balance = st.number_input("Balance", 1000)
    st.write(f"Account: ${balance:,.2f}")

# Fetch Data
@st.cache_data(ttl=60)
def load_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = ta.sma(df['Close'], length=20)
    return df

data = load_data()

if not data.empty:
    # Pro Metrics Row
    current = data['Close'].iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("US30", f"${current:,.2f}")
    col2.metric("Trend", "BULLISH" if current > data['SMA20'].iloc[-1] else "BEARISH")
    col3.metric("AI Status", "Ready", "Optimal")

    # The Pro Chart
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name='SMA 20', line=dict(color='orange')))
    fig.update_layout(template='plotly_dark', height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("✅ AI Signals Active")
