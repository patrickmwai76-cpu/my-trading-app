import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config & Auto-Refresh
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Custom CSS for UI
st.markdown("""
    <style>
    .trend-box { padding: 10px; border-radius: 5px; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold; margin-bottom: 8px; text-align: center; background: rgba(76,175,80,0.1); }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; margin-bottom: 20px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - All Features
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MANAGEMENT")
wallet = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
lots = (wallet * (risk_p/100)) / 50
st.sidebar.info(f"Suggested Lot: {lots:.2f}")

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Main Dashboard Header
st.markdown('<div class="buy-mode">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL</div>', unsafe_allow_html=True)

# 4. Data Logic
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

    # --- Create Triple Subplots (Price, RSI, Volume) ---
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02, 
        row_heights=[0.6, 0.2, 0.2] # Price gets 60%, RSI 20%, Volume 20%
    )

    # Row 1: Candlesticks & FULL Spelling Signals
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Baseline', line=dict(color='orange', width=1)), row=1, col=1)

    recent = df.tail(35)
    for i in range(len(recent)):
        if not pd.isna(recent['SMA_20'].iloc[i]):
            is_buy = recent['Close'].iloc[i] > recent['SMA_20'].iloc[i]
            label = "BUY" if is_buy else "SELL"
            color = "#00FF00" if is_buy else "#FF4B4B"
            y_pos = recent['High'].iloc[i] if is_buy else recent['Low'].iloc[i]
            fig.add_annotation(x=recent.index[i], y=y_pos, text=label, showarrow=False, font=dict(color=color, size=8), yshift=15 if is_buy else -15, row=1, col=1)

    # Row 2: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # Row 3: Volume Bars (The requested feature)
    # Green bars for up candles, Red for down candles
    colors = ['#00FF00' if row['Close'] >= row['Open'] else '#FF4B4B' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.8), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=900, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market data unavailable.")
