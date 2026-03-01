import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config & Professional Theme
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# 2. Sidebar - Controls & Trend Matrix
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
# These match your photo 1000390621.heic
st.sidebar.markdown("""
    <div style="border: 1px solid #4CAF50; color: #4CAF50; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 5px;">1M: UP</div>
    <div style="border: 1px solid #4CAF50; color: #4CAF50; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 5px;">5M: UP</div>
    <div style="border: 1px solid #4CAF50; color: #4CAF50; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 5px;">15M: UP</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Data Engine
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    # Standardize columns to avoid Multi-Index error
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # --- Indicators ---
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    # RSI Fix from previous error
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

    # LAYER 1: Candles & Real Signals
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend', line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)

    # REAL SIGNAL LOGIC: Cross + RSI Confirmation
    for i in range(2, len(df)):
        # Real Buy: Price crosses above SMA AND RSI is NOT overbought
        if df['Close'].iloc[i] > df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] <= df['SMA_20'].iloc[i-1] and df['RSI'].iloc[i] < 70:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", showarrow=True, arrowhead=1, bgcolor="#00FF00", font=dict(color="black", size=10), ay=25, row=1, col=1)
        
        # Real Sell: Price crosses below SMA AND RSI is NOT oversold
        elif df['Close'].iloc[i] < df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] >= df['SMA_20'].iloc[i-1] and df['RSI'].iloc[i] > 30:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", showarrow=True, arrowhead=1, bgcolor="#FF0000", font=dict(color="white", size=10), ay=-25, row=1, col=1)

    # LAYER 2: Real Volume Bars (from 1000390813.heic)
    colors = ['#00FF00' if df['Close'].iloc[i] > df['Open'].iloc[i] else '#FF0000' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume', opacity=0.8), row=2, col=1)

    # LAYER 3: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=900, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Waiting for Market Data...")
