import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Setup
st.set_page_config(page_title="PATRO AI | PRO TERMINAL", layout="wide")
st_autorefresh(interval=30000, key="live_update")

# 2. Sidebar - Risk & Settings
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

# Risk Calculator (Integrated)
st.sidebar.divider()
balance = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 1, 5, 1)
lots = (balance * (risk_p/100)) / 50
st.sidebar.metric("Suggested Lot Size", f"{lots:.2f}")

# 3. Data Engine
df = yf.download("^DJI", period="1d", interval=tf)

if not df.empty:
    # Calculate Simple AI Indicators
    df['SMA'] = df['Close'].rolling(window=10).mean()
    # Buy Signal: Price crosses above SMA | Sell: Price crosses below SMA
    df['Signal'] = 0
    df.loc[df['Close'] > df['SMA'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA'], 'Signal'] = -1

    # --- THE CHARTING ENGINE ---
    # Create 2 Rows: Row 1 for Price, Row 2 for Volume
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # A. Add Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name="US30"), row=1, col=1)

    # B. Add AI Baseline (Moving Average)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name="AI Baseline"), row=1, col=1)

    # C. Add Buy/Sell Signal Arrows
    # Buy Arrows (Green)
    buys = df[df['Signal'] == 1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low'] * 0.999, mode='markers',
                             marker=dict(symbol='triangle-up', size=12, color='#00ff00'), name="BUY SIGNAL"), row=1, col=1)
    
    # Sell Arrows (Red)
    sells = df[df['Signal'] == -1]
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High'] * 1.001, mode='markers',
                             marker=dict(symbol='triangle-down', size=12, color='#ff0000'), name="SELL SIGNAL"), row=1, col=1)

    # D. Add Volume Bars (Row 2)
    colors = ['red' if row['Open'] > row['Close'] else 'green' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

    # Styling
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=700,
                      margin=dict(l=10, r=10, t=10, b=10))
    
    st.plotly_chart(fig, use_container_width=True)

    # Institutional Metrics
    col1, col2 = st.columns(2)
    with col1:
        if df['Signal'].iloc[-1] == 1:
            st.success("💹 CURRENT MODE: BUY (Institutional Accumulation)")
        else:
            st.error("📉 CURRENT MODE: SELL (Institutional Distribution)")
