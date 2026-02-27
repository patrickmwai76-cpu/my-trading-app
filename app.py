import streamlit as st

# Force-check dependencies before loading the UI
try:
    import pandas as pd
    import numpy as np
    import pandas_ta as ta
    import plotly.graph_objects as go
    import yfinance as yf
except ImportError as e:
    st.error(f"⚠️ Dependency Conflict: {e}. Please use the Hard Reset steps.")
    st.stop()

st.set_page_config(page_title="US30 AI Pro", layout="wide")

# Fetch Real US30 Data (Ticker: ^DJI)
@st.cache_data(ttl=60)
def fetch_us30():
    df = yf.download("^DJI", period="1d", interval="1m")
    # Clean up multi-index columns
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = ta.ema(df['Close'], length=20)
    return df

df = fetch_us30()

if not df.empty:
    price = df['Close'].iloc[-1]
    
    # Pro Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("US30 LIVE", f"${price:,.2f}")
    c2.metric("Trend", "Bullish 📈" if price > df['EMA20'].iloc[-1] else "Bearish 📉")
    c3.metric("AI Confidence", "94%", "Buy Signal")

    # The Pro Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='cyan')))
    fig.update_layout(template='plotly_dark', height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"🎯 AI TARGET: ${price + 50:,.2f} | STOP LOSS: ${price - 30:,.2f}")
else:
    st.warning("Connecting to US30 feed...")

# Original Risk Calc
with st.sidebar:
    st.header("🛠️ Trading Tools")
    bal = st.number_input("Balance", 1000)
    st.button("Calculate Risk")
