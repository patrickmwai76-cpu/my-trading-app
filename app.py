import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config & Auto-Refresh (30 Seconds)
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Custom CSS for the Institutional Look
st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; }
    .trend-box { padding: 10px; border-radius: 5px; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold; margin-bottom: 8px; text-align: center; background: rgba(76,175,80,0.1); }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; margin-bottom: 20px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - All Features Included
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

# SOP Checklist
st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("News Guard is CLEAR?")
if s1 and s2: st.sidebar.success("✅ READY TO TRADE")

# Trend Matrix (From your photos)
st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">15M: UP</div>', unsafe_allow_html=True)

# Risk Calculator
st.sidebar.divider()
st.sidebar.subheader("📉 RISK MANAGEMENT")
wallet = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
lots = (wallet * (risk_p/100)) / 50
st.sidebar.info(f"Suggested Lot: {lots:.2f}")

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Main Dashboard
st.markdown('<div class="buy-mode">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v4.0</div>', unsafe_allow_html=True)

# News Guard Section
c_n1, c_n2 = st.columns(2)
c_n1.info("📅 Mon Mar 2 | ISM PMI (10:00 AM)")
c_n2.error("📅 Fri Mar 6 | NFP Jobs (08:30 AM)")

# 4. Data Logic & Technicals
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Subplots (Price on Top, RSI on Bottom)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

    # Add Candles
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Baseline', line=dict(color='orange', width=1)), row=1, col=1)

    # --- FULL SIGNAL LABELS (BUY and SELL) ---
    # This loop puts the full words on every recent candle
    recent = df.tail(35) # Tail(35) keeps the chart clean on mobile screens
    for i in range(len(recent)):
        if not pd.isna(recent['SMA_20'].iloc[i]):
            is_buy = recent['Close'].iloc[i] > recent['SMA_20'].iloc[i]
            label_text = "BUY" if is_buy else "SELL"
            label_color = "#00FF00" if is_buy else "#FF4B4B"
            # Adjusting position so words don't cover the candle body
            y_pos = recent['High'].iloc[i] if is_buy else recent['Low'].iloc[i]
            
            fig.add_annotation(
                x=recent.index[i], 
                y=y_pos, 
                text=label_text, 
                showarrow=False, 
                font=dict(color=label_color, size=8, family="Arial Black"), 
                yshift=15 if is_buy else -15, 
                row=1, col=1
            )

    # RSI (Purple Line)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Offline. Check Connection.")
