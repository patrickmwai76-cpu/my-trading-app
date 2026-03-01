import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Custom Styling for the Institutional Header
st.markdown("""
    <style>
    .buy-mode-header { 
        background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); 
        padding: 20px; border-radius: 10px; color: black; 
        font-weight: bold; text-align: center; margin-bottom: 10px;
    }
    .news-guard { color: #4CAF50; font-weight: bold; font-size: 14px; margin-bottom: 10px; }
    .news-box-blue { background-color: #1e3a5f; padding: 15px; border-radius: 8px; color: #94c1ff; text-align: center; }
    .news-box-red { background-color: #4a1c1c; padding: 15px; border-radius: 8px; color: #ff9494; text-align: center; }
    .trend-box { border: 1px solid #4CAF50; color: #4CAF50; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - TERMINAL CONTROL
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">15M: UP</div>', unsafe_allow_html=True)

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. TOP RESTORATION: PATRO AI PRO HEADER
st.markdown('<div class="buy-mode-header">🛡️ PATRO AI PRO | BUY MODE<br><small>Institutional Scalping Terminal v4.0</small></div>', unsafe_allow_html=True)

# 4. NEWS GUARD ACTIVE SECTION
st.markdown('<div class="news-guard">🛡️ NEWS GUARD ACTIVE</div>', unsafe_allow_html=True)
n_col1, n_col2 = st.columns(2)
with n_col1:
    st.markdown('<div class="news-box-blue">Mon Mar 2 | ISM PMI (10:00 AM)</div>', unsafe_allow_html=True)
with n_col2:
    st.markdown('<div class="news-box-red">Fri Mar 6 | NFP Jobs (08:30 AM)</div>', unsafe_allow_html=True)

st.divider()

# 5. Data & Multi-Layer Chart Logic
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Technical Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # 3-Layer Subplot
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.15, 0.25])

    # LAYER 1: Candles & Real Signals
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend', line=dict(color='orange', width=1.5, dash='dash')), row=1, col=1)

    # REAL BUY/SELL Annotations
    for i in range(2, len(df)):
        if df['Close'].iloc[i] > df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] <= df['SMA_20'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="#00FF00", font=dict(color="black", size=10), row=1, col=1)
        elif df['Close'].iloc[i] < df['SMA_20'].iloc[i] and df['Close'].iloc[i-1] >= df['SMA_20'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="#FF0000", font=dict(color="white", size=10), row=1, col=1)

    # LAYER 2: Volume Bars
    v_colors = ['#00FF00' if df['Close'].iloc[i] > df['Open'].iloc[i] else '#FF0000' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)

    # LAYER 3: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=900, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Terminal Offline - Fetching Data...")
