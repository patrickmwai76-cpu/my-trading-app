import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# 2. Sidebar - Controls & Trend Matrix
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.info("1M: UP | 5M: UP | 15M: UP")

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Data Engine
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Technicals
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. Creating the 3-Layer Chart (Price/Volume/RSI)
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02, 
        row_heights=[0.6, 0.15, 0.25]
    )

    # LAYER 1: Candles & BUY/SELL Labels
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend', line=dict(color='orange', width=1)), row=1, col=1)

    # Logic for Labels (Buy when price crosses SMA up, Sell when crosses down)
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] <= df['SMA_20'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", showarrow=True, arrowhead=1, bgcolor="green", row=1, col=1)
        elif df['Close'].iloc[i] < df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] >= df['SMA_20'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", showarrow=True, arrowhead=1, bgcolor="red", row=1, col=1)

    # LAYER 2: Volume Bars
    colors = ['green' if df['Close'].iloc[i] > df['Open'].iloc[i] else 'red' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

    # LAYER 3: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=900, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Fetching live candles...")
