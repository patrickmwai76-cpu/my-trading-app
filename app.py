import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")

# --- AUTO REFRESH (Every 30 seconds) ---
st_autorefresh(interval=30000, key="patroupdate")

# Custom Dark Theme CSS
st.markdown("""
    <style>
    .trend-box { padding: 12px; border-radius: 5px; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold; margin-bottom: 10px; text-align: center; background-color: rgba(76, 175, 80, 0.05); }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; margin-bottom: 20px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - TERMINAL CONTROL
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

# Trend Matrix (From your photos)
st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">15M: UP</div>', unsafe_allow_html=True)

# Risk Management
st.sidebar.divider()
st.sidebar.subheader("📉 RISK MANAGEMENT")
wallet = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
lots = (wallet * (risk_p/100)) / 50
st.sidebar.info(f"Suggested Lot Size: {lots:.2f}")

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Main Dashboard Data Logic
st.markdown('<div class="buy-mode">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v4.0</div>', unsafe_allow_html=True)

# Fetch Data
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    # Fix for Multi-Index Column Error
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # --- Technical Indicators ---
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    # RSI Calculation (Fixed math from your photo error)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9) 
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. Pro Chart with RSI (From photo 1000390813.heic)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

    # Candlestick Chart (Row 1)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    
    # Add BUY Labels (From your reference image.png)
    buys = df[df['Close'] > df['SMA_20']].tail(1)
    for i, row in buys.iterrows():
        fig.add_annotation(x=i, y=row['Low'], text="BUY", showarrow=True, arrowhead=1, bgcolor="#00ff00", font=dict(color="black", size=12), row=1, col=1)

    # RSI Purple Line (Row 2)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4b4b", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00ffcc", row=2, col=1)

    fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Unavailable. Please wait for the system to refresh.")
