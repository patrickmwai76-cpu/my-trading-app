import streamlit as st

# --- SAFE IMPORT CHECK ---
try:
    import pandas as pd
    import numpy as np
    import pandas_ta as ta
    import plotly.graph_objects as go
    import yfinance as yf
except ImportError as e:
    st.error(f"Dependency Error: {e}. Please ensure requirements.txt is correct.")
    st.stop()

st.set_page_config(page_title="US30 AI Pro Live", layout="wide")

# Fetch Real US30 Data (Ticker: ^DJI)
@st.cache_data(ttl=60)
def get_live_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = ta.sma(df['Close'], length=20)
    return df

data = get_live_data()

if not data.empty:
    curr = data['Close'].iloc[-1]
    
    # Pro Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("US30 LIVE", f"${curr:,.2f}")
    c2.metric("Trend", "BULLISH 📈" if curr > data['SMA20'].iloc[-1] else "BEARISH 📉")
    c3.metric("AI Status", "Ready", "Optimal Signal")

    # Pro Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name='SMA 20', line=dict(color='orange')))
    fig.update_layout(template='plotly_dark', height=400, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"🚀 AI SIGNAL: {'BUY' if curr > data['SMA20'].iloc[-1] else 'SELL'} @ {curr:,.2f}")
